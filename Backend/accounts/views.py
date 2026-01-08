from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializer import UserSerializer, CustomTokenObtainPairSerializer 
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Sum
from decimal import Decimal
from django.db import transaction
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.utils import timezone
import hmac
import hashlib
import json
from django.conf import settings
from .models import SolicitacaoPagamento, Transacao, CustomUser, MetricasDiarias
from games.models import Aposta
from .services import SkalePayService


class RegisterView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Retorna 201 Created e os dados (sem a senha)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # Retorna 400 Bad Request e explica o erro (ex: "CPF já existe")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class DashboardFinanceiroView(APIView):
    """
    Retorna métricas híbridas: 
    - Histórico (D-1 para trás): Leitura rápida da tabela MetricasDiarias.
    - Tempo Real (D0): Cálculo on-the-fly apenas do dia atual.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        hoje = timezone.localdate()

        # A. DADOS HISTÓRICOS (Soma tudo o que já foi consolidado na tabela MetricasDiarias)
        # Como o banco já somou os dias anteriores, aqui só somamos os totais da tabela de resumo.
        historico = MetricasDiarias.objects.aggregate(
            total_apostado=Sum('total_apostado'),
            total_pago=Sum('total_premios'),
            receita_liquida=Sum('receita_liquida'),
            depositos=Sum('total_deposito'),
            saques=Sum('total_saque'),
            users_total=Sum('novos_usuarios') 
        )

        # Trata nulos (caso o sistema seja novo e não tenha histórico ainda)
        h_apostado = historico['total_apostado'] or 0
        h_pago = historico['total_pago'] or 0
        h_receita = historico['receita_liquida'] or 0
        h_depositos = historico['depositos'] or 0
        h_saques = historico['saques'] or 0

        # B. DADOS DE HOJE (Tempo Real - Calcula na hora, mas só de 1 dia)
        # Financeiro Hoje
        dep_hoje = Transacao.objects.filter(tipo='DEPOSITO', data__date=hoje).aggregate(Sum('valor'))['valor__sum'] or 0
        saq_hoje = Transacao.objects.filter(tipo='SAQUE', data__date=hoje).aggregate(Sum('valor'))['valor__sum'] or 0
        
        # Apostas Hoje
        apostas_hoje = Aposta.objects.filter(criado_em__date=hoje).aggregate(Sum('valor'))['valor__sum'] or 0
        premios_hoje = Aposta.objects.filter(ganhou=True, criado_em__date=hoje).aggregate(Sum('valor_premio'))['valor_premio__sum'] or 0
        lucro_hoje = apostas_hoje - premios_hoje
        
        novos_hoje = CustomUser.objects.filter(date_joined__date=hoje).count()

        # C. CONSOLIDAÇÃO (Histórico + Hoje)
        total_apostado_geral = h_apostado + apostas_hoje
        total_pago_geral = h_pago + premios_hoje
        house_edge_geral = h_receita + lucro_hoje # Lucro Operacional Bruto
        
        # Count total é sempre rápido no Postgres, não precisa de histórico
        total_users = CustomUser.objects.count() 
        
        # Saldo Tesouraria (Depositos Reais - Saques Reais)
        saldo_tesouraria = (h_depositos + dep_hoje) - (h_saques + saq_hoje)

        return Response({
            "hoje": {
                "faturamento": apostas_hoje,
                "premios_pagos": premios_hoje,
                "lucro_liquido": lucro_hoje,
                "novos_usuarios": novos_hoje,
                "depositos": dep_hoje,
                "saques": saq_hoje
            },
            "acumulado": {
                "total_apostado": total_apostado_geral,
                "total_pago": total_pago_geral,
                "lucro_operacional": house_edge_geral,
                "margem_lucro": f"{((house_edge_geral/total_apostado_geral)*100):.1f}%" if total_apostado_geral > 0 else "0%"
            },
            "tesouraria": {
                "total_depositado": h_depositos + dep_hoje,
                "total_sacado": h_saques + saq_hoje,
                "saldo_em_conta": saldo_tesouraria
            },
            "usuarios_ativos": total_users
        })
    
    
class GerarDepositoPixView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        valor = request.data.get('valor')
        if not valor: return Response({"erro": "Informe o valor"}, status=400)

        try:
            resp = SkalePayService.gerar_pedido_deposito(request.user, valor)
            
            # Ajuste de campos baseado no padrão comum de resposta
            qr_code = resp.get('pixQrCode', '') or resp.get('emv', '') 
            id_skale = resp.get('id')
            
            SolicitacaoPagamento.objects.create(
                usuario=request.user,
                tipo='DEPOSITO',
                valor=valor,
                status='PENDENTE',
                id_externo=id_skale,
                qr_code=qr_code
            )
            
            return Response({
                "qr_code": qr_code,
                "id_transacao": id_skale
            })
        except Exception as e:
            return Response({"erro": str(e)}, status=500)
    
class SolicitarSaqueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        valor = Decimal(str(request.data.get('valor')))
        chave_pix = request.data.get('chave_pix')
        usuario = request.user

        if not chave_pix:
            return Response({"erro": "Chave Pix obrigatória"}, status=400)

        try:
            # Bloco Atômico: Ou tudo dá certo, ou nada acontece (Rollback)
            with transaction.atomic():
                user_travado = CustomUser.objects.select_for_update().get(id=usuario.id)

                # 1. Validações Locais
                if user_travado.saldo < valor:
                    return Response({"erro": "Saldo insuficiente na plataforma."}, status=400)
                
                if not user_travado.pode_sacar():
                    return Response({"erro": "Rollover pendente. Aposte mais para liberar o saque."}, status=400)

                # 2. Prepara a Solicitação (Estado Inicial: PENDENTE)
                # Criamos antes para ter um ID para mandar no 'externalRef'
                solicitacao = SolicitacaoPagamento.objects.create(
                    usuario=user_travado,
                    tipo='SAQUE',
                    valor=valor,
                    status='PENDENTE',
                    qr_code=chave_pix 
                )

                # 3. CHAMA A SKALEPAY (A Integração Real)
                # Se der erro aqui (ex: chave inválida), vai pro 'except' e desfaz a criação acima
                recibo = SkalePayService.solicitar_saque_pix(
                    usuario=user_travado, 
                    valor_reais=valor, 
                    chave_pix=chave_pix,
                    referencia_interna=solicitacao.id
                )

                # 4. Sucesso! Efetiva o Débito e Aprova
                saldo_anterior = user_travado.saldo
                user_travado.saldo -= valor
                user_travado.save()

                solicitacao.status = 'APROVADO'
                solicitacao.id_externo = recibo.get('id') # Salva o ID da transferência real
                solicitacao.save()

                Transacao.objects.create(
                    usuario=user_travado,
                    tipo='SAQUE',
                    valor=valor,
                    saldo_anterior=saldo_anterior,
                    saldo_posterior=user_travado.saldo,
                    descricao=f"Saque Pix Automático",
                    origem_solicitacao=solicitacao
                )

            return Response({
                "mensagem": "Saque enviado com sucesso!",
                "comprovante_banco": solicitacao.id_externo,
                "novo_saldo": user_travado.saldo
            })

        except Exception as e:
            # Em caso de erro na API ou Validação, retorna msg amigável
            # O transaction.atomic() garante que o saldo não muda
            return Response({"erro": "Falha no processamento", "detalhe": str(e)}, status=400)
        
class SkalePayWebhookView(APIView):
    """
    Recebe notificações assíncronas da SkalePay.
    Valida a assinatura (HMAC), garante idempotência e libera saldo/bônus.
    """
    authentication_classes = [] # Webhooks são públicos (autenticados por assinatura)
    permission_classes = [AllowAny]

    def post(self, request):
        # 1. SEGURANÇA: Verificar Assinatura (Evita hackers forjando depósitos)
        # O cabeçalho exato depende da doc da SkalePay, mas geralmente é 'X-Signature' ou similar.
        skalepay_signature = request.headers.get('X-SkalePay-Signature', '')
        secret = getattr(settings, 'SKALEPAY_SECRET_KEY', '').encode('utf-8')
        
        # Se não configurou a chave, loga erro crítico e rejeita (Fail Safe)
        if not secret:
            return Response({"erro": "Configuração de servidor incompleta (Secret Key)"}, status=500)

        # Recria a assinatura com o payload recebido e compara
        payload_body = request.body
        expected_signature = hmac.new(secret, payload_body, hashlib.sha256).hexdigest()
        
        # Comparação segura contra timing attacks
        if not hmac.compare_digest(skalepay_signature, expected_signature):
             # Em produção, retorne 200 ou 403 silencioso para não dar dicas ao atacante
            return Response({"erro": "Assinatura inválida"}, status=status.HTTP_403_FORBIDDEN)

        # 2. PROCESSAMENTO
        dados = request.data
        id_externo = dados.get('transaction_id') # ID da SkalePay
        status_pagamento = dados.get('status')   # ex: 'PAID', 'FAILED', 'CANCELED'
        
        if not id_externo:
            return Response({"erro": "Payload inválido"}, status=400)

        try:
            with transaction.atomic():
                # Busca a intenção de pagamento (criada quando o usuário clicou em "Depositar")
                # Se for um depósito direto (sem pedido prévio), criamos agora (Opcional, mas seguro)
                solicitacao, created = SolicitacaoPagamento.objects.select_for_update().get_or_create(
                    id_externo=id_externo,
                    defaults={
                        'valor': Decimal(str(dados.get('amount', '0.00'))),
                        'tipo': 'DEPOSITO',
                        'usuario_id': dados.get('customer_custom_id'), # Precisamos enviar o ID do user na criação do pix
                        'status': 'PENDENTE'
                    }
                )

                # IDEMPOTÊNCIA: Se já processamos, para tudo.
                if solicitacao.status in ['APROVADO', 'RECUSADO', 'CANCELADO']:
                    return Response({"msg": "Webhook já processado anteriormente"}, status=200)

                if status_pagamento == 'PAID':
                    self._efetivar_aprovacao(solicitacao)
                elif status_pagamento in ['FAILED', 'CANCELED']:
                    solicitacao.status = 'RECUSADO'
                    solicitacao.save()

            return Response({"status": "received"}, status=200)

        except Exception as e:
            # Logar o erro real aqui
            return Response({"erro": "Erro interno ao processar webhook"}, status=500)

    def _efetivar_aprovacao(self, solicitacao):
        """Lógica Blindada de Crédito (Ledger)"""
        usuario = solicitacao.usuario
        valor = solicitacao.valor
        
        # 1. Aplica Regras de Negócio (Bônus)
        bonus = usuario.aplicar_bonus_deposito(valor)
        
        # 2. Atualiza Saldo (Atomicamente protegido pelo caller)
        saldo_anterior = usuario.saldo
        usuario.saldo += valor + bonus
        usuario.save()
        
        # 3. Registra Fato Contábil (Transacao) e Vincula à Solicitação
        tx_deposito = Transacao.objects.create(
            usuario=usuario,
            tipo='DEPOSITO',
            valor=valor,
            saldo_anterior=saldo_anterior,
            saldo_posterior=saldo_anterior + valor,
            descricao=f"Depósito via Pix (SkalePay: {solicitacao.id_externo})",
            origem_solicitacao=solicitacao 
        )
        
        if bonus > 0:
            Transacao.objects.create(
                usuario=usuario,
                tipo='BONUS',
                valor=bonus,
                saldo_anterior=tx_deposito.saldo_posterior,
                saldo_posterior=usuario.saldo,
                descricao="Bônus Automático de Depósito"
            )

        # 4. Finaliza Ciclo de Vida da Solicitação
        solicitacao.status = 'APROVADO'
        solicitacao.save()