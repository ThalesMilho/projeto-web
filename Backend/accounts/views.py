# Python / infra
import csv
import hmac
import hashlib
from decimal import Decimal


from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiExample

# Django
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.db import transaction, DatabaseError
from django.db.models import Sum, Count, Q

# DRF
from rest_framework import status, viewsets, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.views import TokenObtainPairView

# Local
from .models import SolicitacaoPagamento, Transacao, CustomUser, MetricasDiarias
from .services import SkalePayService
from .serializer import (
    UserSerializer,
    CustomTokenObtainPairSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    SolicitacaoPagamentoAdminSerializer,
    AnaliseSolicitacaoSerializer,
    RiscoIPSerializer,
    DepositoSerializer 
)

from games.models import Aposta, ParametrosDoJogo

# Diagnostic imports
import requests
import traceback
import logging
import json
import os

# Logger for Render/console
logger = logging.getLogger('django')

from .gateways.skalepay import SkalePayClient, SkalePayError

# Diagnostic endpoint: Deep connectivity check to SkalePay
@csrf_exempt
def testar_conexao_skalepay(request):
    """
    Endpoint de Diagnóstico "Deep Dive" v2.0
    Objetivo: Validar conectividade E2E com SkalePay sem derrubar o worker.
    """

    report = {
        "etapa_1_ambiente": "N/A",
        "etapa_2_configuracao": "N/A",
        "etapa_3_conectividade": "N/A",
        "timestamp_server": "",
        "dados_tecnicos": {}
    }

    print("--- [QA DIAGNOSTIC] INICIANDO TESTE SKALEPAY ---")

    try:
        env_key = os.getenv('SKALEPAY_SECRET_KEY')
        report['etapa_1_ambiente'] = "OK" if env_key else "FALHA - Variável de ambiente ausente"

        django_key = getattr(settings, 'SKALEPAY_SECRET_KEY', None)
        final_key = django_key or env_key

        masked_key = "NULA"
        if final_key:
            if len(final_key) > 8:
                masked_key = f"{final_key[:4]}...{final_key[-4:]}"
            else:
                masked_key = "***CURTA***"

        report['dados_tecnicos']['chave_identificada'] = masked_key

        if not final_key or final_key == '123456':
            report['etapa_2_configuracao'] = "CRÍTICO: Chave não configurada ou é placeholder"
            return JsonResponse(report, status=500)

        report['etapa_2_configuracao'] = "OK - Chave carregada"

        target_url = "https://api.conta.skalepay.com.br/v1/balance"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "DiagnosticBot/2.0 (Render; Django)"
        }

        auth = (final_key, "")

        print(f"--- [QA DIAGNOSTIC] Disparando Request para: {target_url}")

        response = requests.get(
            target_url,
            auth=auth,
            headers=headers,
            timeout=10,
            verify=True
        )

        report['dados_tecnicos']['http_status'] = response.status_code
        report['dados_tecnicos']['latency_ms'] = response.elapsed.total_seconds() * 1000

        try:
            response_json = response.json()
        except json.JSONDecodeError:
            response_json = {"raw_text": response.text[:200]}

        report['dados_tecnicos']['response_body'] = response_json

        if response.status_code == 200:
            report['etapa_3_conectividade'] = "SUCESSO - Conexão estabelecida e autenticada"
            status_code = 200
        elif response.status_code == 401:
            report['etapa_3_conectividade'] = "FALHA - Acesso Negado (Chave Incorreta)"
            status_code = 401
        elif response.status_code == 403:
            report['etapa_3_conectividade'] = "BLOQUEIO - WAF/IP Bloqueado pela SkalePay"
            status_code = 403
        else:
            report['etapa_3_conectividade'] = f"ALERTA - Status inesperado: {response.status_code}"
            status_code = 502

        print("--- [QA DIAGNOSTIC] FINALIZADO COM SUCESSO ---")
        return JsonResponse(report, status=status_code)

    except requests.exceptions.ConnectTimeout:
        print("--- [QA DIAGNOSTIC] ERRO: TIMEOUT ---")
        report['etapa_3_conectividade'] = "TIMEOUT - Servidor não respondeu em 10s"
        report['sugestao'] = "Verifique se o IP do Render está na whitelist da SkalePay."
        return JsonResponse(report, status=504)

    except requests.exceptions.SSLError as e:
        print(f"--- [QA DIAGNOSTIC] ERRO: SSL -> {str(e)}")
        report['etapa_3_conectividade'] = "ERRO SSL - Falha no certificado de segurança"
        report['dados_tecnicos']['erro_detalhe'] = str(e)
        return JsonResponse(report, status=502)

    except Exception as e:
        print("--- [QA DIAGNOSTIC] EXCEPTION FATAL ---")
        traceback.print_exc()

        report['etapa_3_conectividade'] = "CRASH INTERNO"
        report['dados_tecnicos']['erro_tipo'] = str(type(e))
        report['dados_tecnicos']['erro_msg'] = str(e)
        report['dados_tecnicos']['traceback'] = traceback.format_exc()

        return JsonResponse(report, status=500)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Registro de Usuário",
        request=UserSerializer, # Aqui é fácil, já temos serializer!
        responses={201: UserSerializer}
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # --- NOVO: Captura de IP para Segurança ---
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            user.ip_registro = ip
            user.ultimo_ip = ip
            user.save()
            # ------------------------------------------

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Executa o login padrão
        response = super().post(request, *args, **kwargs)
        
        # Se logou com sucesso, atualiza o IP
        if response.status_code == 200:
            try:
                user = CustomUser.objects.get(cpf_cnpj=request.data.get('cpf_cnpj'))
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')
                user.ultimo_ip = ip
                user.save()
            except Exception:
                pass # Não trava o login se der erro no IP
                
        return response

class DashboardFinanceiroView(APIView):
    """
    Dashboard Profissional com Filtros, Segurança e Inteligência de Negócio.
    Aceita query params: ?inicio=YYYY-MM-DD&fim=YYYY-MM-DD
    """
    # Em produção, use [IsAdminUser]. Para testes rápidos, [AllowAny] (Cuidado!)
    permission_classes = [IsAdminUser]
    authentication_classes = []
    @extend_schema(summary="Dashboard Financeiro", responses={200: OpenApiTypes.OBJECT}) 
    def get(self, request):
        hoje = timezone.localdate()
        
        # 1. FILTROS (Padrão: 30 dias)
        data_inicio_str = request.query_params.get('inicio')
        data_fim_str = request.query_params.get('fim')
        
        if data_inicio_str:
            data_inicio = timezone.datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        else:
            data_inicio = hoje - timezone.timedelta(days=30)
            
        if data_fim_str:
            data_fim = timezone.datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        else:
            data_fim = hoje

        # 2. DADOS HISTÓRICOS (Base SQL Otimizada)
        qs_historico = MetricasDiarias.objects.filter(data__gte=data_inicio, data__lt=hoje)
        
        resumo_hist = qs_historico.aggregate(
            apostado=Sum('total_apostado'),
            premios=Sum('total_premios'),
            ggr=Sum('house_edge_valor'),
            depositos=Sum('total_deposito_valor'),
            depositos_qtd=Sum('total_deposito_qtd'),
            saques=Sum('total_saque_valor'),
            bonus=Sum('total_bonus_concedido'),
            ftds=Sum('ftds_qtd'),
            novos=Sum('novos_usuarios')
        )

        # 3. GRÁFICO (Evolução Diária)
        grafico_evolucao = []
        for dia in qs_historico.order_by('data'):
            grafico_evolucao.append({
                "data": dia.data.strftime('%d/%m'),
                "depositos": float(dia.total_deposito_valor),
                "saques": float(dia.total_saque_valor),
                "lucro": float(dia.house_edge_valor)
            })

        # 4. CÁLCULO "HOJE" (Real-Time)
        incluir_hoje = (data_inicio <= hoje <= data_fim)
        
        if incluir_hoje:
            dep_hoje = Transacao.objects.filter(tipo='DEPOSITO', data__date=hoje).aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            dep_qtd_hoje = Transacao.objects.filter(tipo='DEPOSITO', data__date=hoje).count()
            saq_hoje = Transacao.objects.filter(tipo='SAQUE', data__date=hoje).aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            bonus_hoje = Transacao.objects.filter(tipo='BONUS', data__date=hoje).aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            
            apostas_hoje = Aposta.objects.filter(criado_em__date=hoje).aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            premios_hoje = Aposta.objects.filter(ganhou=True, criado_em__date=hoje).aggregate(Sum('valor_premio'))['valor_premio__sum'] or Decimal(0)
            lucro_hoje = apostas_hoje - premios_hoje
            
            ftd_hoje = CustomUser.objects.filter(data_primeiro_deposito__date=hoje).count()
            novos_hoje = CustomUser.objects.filter(date_joined__date=hoje).count()
            
            # Adiciona 'Hoje' no gráfico também
            grafico_evolucao.append({
                "data": "Hoje",
                "depositos": float(dep_hoje),
                "saques": float(saq_hoje),
                "lucro": float(lucro_hoje)
            })
        else:
            dep_hoje = saq_hoje = bonus_hoje = apostas_hoje = premios_hoje = lucro_hoje = Decimal(0)
            dep_qtd_hoje = ftd_hoje = novos_hoje = 0

        # 5. TOTAIS CONSOLIDADOS
        total_dep = (resumo_hist['depositos'] or Decimal(0)) + dep_hoje
        total_dep_qtd = (resumo_hist['depositos_qtd'] or 0) + dep_qtd_hoje
        total_saq = (resumo_hist['saques'] or Decimal(0)) + saq_hoje
        total_ggr = (resumo_hist['ggr'] or Decimal(0)) + lucro_hoje
        total_apostado = (resumo_hist['apostado'] or Decimal(0)) + apostas_hoje
        total_ftds = (resumo_hist['ftds'] or 0) + ftd_hoje
        total_novos = (resumo_hist['novos'] or 0) + novos_hoje

        # 6. GAP RESOLVIDO: CONTAGEM DE FILA (PENDÊNCIAS)
        fila_depositos = SolicitacaoPagamento.objects.filter(tipo='DEPOSITO', status='PENDENTE').count()
        fila_saques = SolicitacaoPagamento.objects.filter(tipo='SAQUE', status='PENDENTE').count()
        
        # GAP RESOLVIDO: ALERTA DE RISCO (Multi-contas IP)
        # Conta quantos IPs tem mais de 1 usuário associado
        ips_duplicados = CustomUser.objects.values('ultimo_ip').annotate(
            total_contas=Count('id')
        ).filter(total_contas__gt=1).count()
        
        alertas_risco = ips_duplicados

        # GAP 3: Projeção de Receita (Forecast Simples)
        # Lógica: Pegamos a média de GGR (Lucro) dos últimos 7 dias e projetamos para os próximos 7.
        
        # 1. Busca os últimos 7 dias fechados
        data_limite_projecao = hoje - timezone.timedelta(days=7)
        qs_projecao = MetricasDiarias.objects.filter(data__gte=data_limite_projecao, data__lt=hoje)
        
        qtd_dias_base = qs_projecao.count()
        soma_ggr_7dias = qs_projecao.aggregate(Sum('house_edge_valor'))['house_edge_valor__sum'] or Decimal(0)
        
        # Adicionamos o dia de HOJE na média para ser mais preciso (se tiver dados)
        if incluir_hoje:
            soma_ggr_7dias += lucro_hoje
            qtd_dias_base += 1
            
        media_diaria_ggr = soma_ggr_7dias / qtd_dias_base if qtd_dias_base > 0 else Decimal(0)
        
        # Projeção para os próximos 7 e 30 dias
        projecao_7d = media_diaria_ggr * 7
        projecao_30d = media_diaria_ggr * 30

        # --- NOVOS CÁLCULOS (Onde a mágica acontece) ---

        # A. Ticket Médio & Conversão
        ticket_medio_dep = total_dep / total_dep_qtd if total_dep_qtd > 0 else 0
        taxa_conversao_ftd = (total_ftds / total_novos * 100) if total_novos > 0 else 0.0
        rentabilidade_casa = (total_ggr / total_apostado * 100) if total_apostado > 0 else 0.0

        # [CORREÇÃO ITEM 6]: Recuperar JSONs Operacionais (Apenas do dia de ontem/hoje ou agregado)
        # Simplificação: Pegamos o mapa de calor do último dia fechado para exibir "Tendência de Horário"
        ultimo_fechamento = MetricasDiarias.objects.order_by('-data').first()
        mapa_calor = ultimo_fechamento.mapa_calor_horas if ultimo_fechamento else {}
        top_modalidades = ultimo_fechamento.performance_modalidades if ultimo_fechamento else {}

        # B. Churn (Rotatividade) & Retenção
        # Usuários ativos = Fizeram aposta nos últimos 30 dias
        corte_30d = timezone.now() - timezone.timedelta(days=30)
        total_users_base = CustomUser.objects.count()
        
        # Query otimizada para contar IDs únicos na tabela de Apostas
        ativos_30d = Aposta.objects.filter(criado_em__gte=corte_30d).values('usuario').distinct().count()
        
        taxa_retencao = (ativos_30d / total_users_base * 100) if total_users_base > 0 else 0.0
        taxa_churn = 100.0 - taxa_retencao

        # C. Crescimento Mês a Mês (Growth Rate)
        # Compara GGR dos ultimos 30 dias vs 30 dias anteriores
        inicio_mes_passado = corte_30d - timezone.timedelta(days=30)
        
        ggr_mes_passado = MetricasDiarias.objects.filter(
            data__gte=inicio_mes_passado, 
            data__lt=corte_30d
        ).aggregate(Sum('house_edge_valor'))['house_edge_valor__sum'] or Decimal(0)

        # Para ser justo, o GGR atual deve considerar também os últimos 30 dias (histórico + hoje)
        # Como simplificação, usamos o total_ggr calculado acima se o filtro for o padrão de 30 dias
        crescimento_percent = 0.0
        if ggr_mes_passado > 0:
            crescimento_percent = ((total_ggr - ggr_mes_passado) / ggr_mes_passado) * 100

        return Response({
            "periodo": {"inicio": data_inicio, "fim": data_fim},
            "resumo": {
                "depositos": total_dep,
                "saques": total_saq,
                "fluxo_caixa": total_dep - total_saq,
                "lucro_liquido": total_ggr,
                "total_apostado": total_apostado,
                "ftds": total_ftds,
                "novos_usuarios": total_novos
            },
            "kpis_estrategicos": {
                "ticket_medio_deposito": round(float(ticket_medio_dep), 2),
                "taxa_conversao_ftd": round(float(taxa_conversao_ftd), 2),
                "rentabilidade_casa_percent": round(float(rentabilidade_casa), 2),
                "churn_estimado_percent": round(float(taxa_churn), 2),
                "retencao_usuarios_percent": round(float(taxa_retencao), 2),
                "crescimento_mensal_percent": round(float(crescimento_percent), 2)
            },
            "inteligencia": {
                "projecao_lucro_30d": round(float(projecao_30d), 2),
                "tendencia": "Alta" if crescimento_percent > 0 else "Baixa"
            },
            "operacional": {
                "mapa_calor": mapa_calor,
                "top_modalidades": top_modalidades,
                "alertas_risco": alertas_risco,
                "fila_saques": fila_saques,
                "fila_depositos": fila_depositos
            },
            "grafico": grafico_evolucao
        })
    
    
class GerarDepositoPixView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Gerar Depósito Pix",
        request=DepositoSerializer,
        responses={200: OpenApiTypes.OBJECT}
    )
    def post(self, request):
        serializer = DepositoSerializer(data=request.data)
        if serializer.is_valid():
            valor = serializer.validated_data['valor']
            try:
                resposta_gateway = SkalePayService.gerar_pedido_deposito(request.user, valor)

                # Cria a Solicitação no Banco
                solicitacao = SolicitacaoPagamento.objects.create(
                    usuario=request.user,
                    tipo='DEPOSITO',
                    valor=valor,
                    status='PENDENTE',
                    id_externo=str(resposta_gateway.get('transaction_id')),
                    qr_code=resposta_gateway.get('qr_code'),
                    qr_code_url=resposta_gateway.get('qr_code_url')
                )

                # Cria o registro financeiro (Extrato)
                Transacao.objects.create(
                    usuario=request.user,
                    tipo='DEPOSITO',
                    valor=valor,
                    saldo_anterior=request.user.saldo,
                    saldo_posterior=request.user.saldo,
                    descricao=f"Aguardando Pagamento Pix",
                    origem_solicitacao=solicitacao
                )

                return Response({
                    "sucesso": True,
                    "transaction_id": resposta_gateway.get('transaction_id'),
                    "qr_code": resposta_gateway.get('qr_code'),
                    "qr_code_url": resposta_gateway.get('qr_code_url'),
                    "expira_em": resposta_gateway.get('expiration')
                }, status=200)

            except Exception as e:
                return Response({
                    "erro": "Falha ao gerar Pix",
                    "detalhes": str(e)
                }, status=500)
            
        return Response(serializer.errors, status=400)
    
class SolicitarSaqueView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Solicitar Saque Pix",
        description="Solicita um saque. Verifica saldo, rollover, travas de tempo e risco. Tenta pagar automático ou envia para análise.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'valor': {'type': 'number', 'example': 150.00},
                    'chave_pix': {'type': 'string', 'example': '12345678900'}
                },
                'required': ['valor', 'chave_pix']
            }
        },
        responses={
            200: {'description': 'Saque realizado com sucesso (Automático)'},
            202: {'description': 'Saque em análise (Valor alto ou Risco)'},
            400: {'description': 'Saldo insuficiente ou Rollover pendente'},
            403: {'description': 'Travamento de segurança (Tempo pós-depósito)'}
        }
    )
    def post(self, request):
        # 1. Validação Básica
        try:
            valor = Decimal(str(request.data.get('valor')))
            chave_pix = request.data.get('chave_pix')
            if not chave_pix or valor <= 0:
                raise ValueError
        except:
            return Response({"detail": "Dados inválidos."}, status=400)

        # 2. Proteção de Liquidez (Fail Fast)
        saldo_banca = SkalePayService.consultar_saldo_banca()
        if saldo_banca is not None and saldo_banca < float(valor):
            return Response({"detail": "Saque indisponível momentaneamente."}, status=503)

        # 3. Transação Atômica: Regras, Bloqueio e Débito
        try:
            with transaction.atomic():
                user = CustomUser.objects.select_for_update().get(id=request.user.id)

                # --- REGRA A: Saldo ---
                if user.saldo < valor:
                    return Response({"detail": "Saldo insuficiente."}, status=400)

                # --- REGRA B: Rollover ---
                if hasattr(user, 'pode_sacar') and not user.pode_sacar():
                    return Response({"detail": "Rollover pendente."}, status=400)

                # --- REGRA C: Trava de Tempo (GAP 1) ---
                ultimo_deposito = Transacao.objects.filter(usuario=user, tipo='DEPOSITO').order_by('-data').first()
                if ultimo_deposito:
                    delta = timezone.now() - ultimo_deposito.data
                    if delta.total_seconds() < 60:
                        return Response({"detail": "Aguarde processamento do depósito."}, status=403)

                # --- REGRA D: Valor Alto (GAP 2) ---
                if valor > 500:
                    SolicitacaoPagamento.objects.create(
                        usuario=user, tipo='SAQUE', valor=valor,
                        status='EM_ANALISE', chave_pix=chave_pix
                    )
                    user.saldo -= valor
                    user.save()
                    return Response({"detail": "Saque em análise de segurança."}, status=202)

                # --- FLUXO AUTOMÁTICO ---
                solicitacao = SolicitacaoPagamento.objects.create(
                    usuario=user, tipo='SAQUE', valor=valor,
                    status='PROCESSANDO', chave_pix=chave_pix
                )
                user.saldo -= valor
                user.save()
                
                Transacao.objects.create(
                    usuario=user, tipo='SAQUE', valor=valor,
                    saldo_anterior=user.saldo + valor, saldo_posterior=user.saldo,
                    descricao="Solicitação de Saque", origem_solicitacao=solicitacao
                )

        except DatabaseError:
            return Response({"detail": "Erro de concorrência. Tente novamente."}, status=409)

        # 4. Comunicação Externa (Fora da Transação do Banco)
        import requests
        try:
            dados_api = SkalePayService.solicitar_saque_pix(
                usuario=request.user, valor_reais=valor,
                chave_pix=chave_pix, referencia_interna=solicitacao.id
            )
            # Sucesso
            solicitacao.status = 'APROVADO'
            solicitacao.id_externo = dados_api.get('id')
            solicitacao.save()
            return Response({"detail": "Saque enviado!"})

        except requests.exceptions.ReadTimeout:
            # CRÍTICO: Se der timeout, NÃO estornamos. O dinheiro pode ter saído.
            solicitacao.analise_motivo = "Timeout Banco. Auditoria pendente."
            solicitacao.save()
            return Response({"detail": "Processando confirmação bancária."}, status=202)

        except Exception as e:
            # Erro definitivo (400, 401, etc) -> Estorno Seguro
            with transaction.atomic():
                user = CustomUser.objects.select_for_update().get(id=request.user.id)
                user.saldo += valor
                user.save()
                
                solicitacao.status = 'RECUSADO'
                solicitacao.analise_motivo = str(e)
                solicitacao.save()
                
                Transacao.objects.create(
                    usuario=user, tipo='ESTORNO', valor=valor,
                    saldo_anterior=user.saldo - valor, saldo_posterior=user.saldo,
                    descricao="Estorno (Falha Envio)", origem_solicitacao=solicitacao
                )
            return Response({"detail": "Falha no envio. Valor estornado."}, status=502)
    
class SkalePayWebhookView(APIView):
    """
    Recebe notificações (Callback) da SkalePay quando um Pix é pago.
    """
    authentication_classes = [] # Webhooks são públicos (mas assinados)
    permission_classes = [AllowAny]
    @extend_schema(
        summary="Webhook de Pagamento",
        request={'application/json': {'type': 'object', 'additionalProperties': True}},
        responses={200: OpenApiTypes.OBJECT}
    )
    def post(self, request):
        # 1. SEGURANÇA: Verificar Assinatura (HMAC SHA-256)
        #skalepay_signature = request.headers.get('X-SkalePay-Signature', '')
        #secret = getattr(settings, 'SKALEPAY_SECRET_KEY', '').encode('utf-8')
        
        # Só valida se tiver chave configurada (Evita erro em dev sem chave)
        #if secret:
        payload_body = request.body
        expected_signature = hmac.new(secret, payload_body, hashlib.sha256).hexdigest()
            
        # Comparação segura contra 'timing attacks'
        if not hmac.compare_digest(skalepay_signature, expected_signature):
            return Response({"erro": "Assinatura inválida/Forjada"}, status=403)

        # 2. LER DADOS
        dados = request.data
        data = dados.get('data', {})  # Webhook payload has nested 'data' field
        id_externo = data.get('id') # ID da transação na SkalePay
        status_pagamento = data.get('status')   # ex: 'paid', 'failed'
        metadata = data.get('metadata', {})
        usuario_id = metadata.get('usuario_id')  # Get user ID from metadata

        if usuario_id is None:
            logger.error("Usuario nao identificado no metadata", extra={"payload": dados})
            return Response({"erro": "Usuario nao identificado no metadata"}, status=400)
        
        if not id_externo:
            return Response({"erro": "Payload sem ID"}, status=400)

        try:
            with transaction.atomic():
                # Busca a solicitação no banco travando a linha (Lock)
                solicitacao, created = SolicitacaoPagamento.objects.select_for_update().get_or_create(
                    id_externo=id_externo,
                    defaults={
                        # Se não existir (Depósito direto sem pedir no site), cria agora
                        'valor': Decimal(str(data.get('amount', '0.00'))) / 100,  # Convert from cents
                        'tipo': 'DEPOSITO',
                        'usuario_id': usuario_id,
                        'status': 'PENDENTE'
                    }
                )

                # IDEMPOTÊNCIA: Se já foi processado, retorna OK e não faz nada
                if solicitacao.status in ['APROVADO', 'RECUSADO', 'CANCELADO']:
                    return Response({"msg": "Já processado anteriormente"}, status=200)

                # 3. DECISÃO
                if status_pagamento == 'paid':
                    self._efetivar_aprovacao(solicitacao)
                elif status_pagamento in ['failed', 'canceled']:
                    solicitacao.status = 'RECUSADO'
                    solicitacao.save()

            return Response({"status": "received"}, status=200)

        except Exception as e:
            # Em produção, use logging.error(str(e))
            return Response({"erro": "Erro interno ao processar"}, status=500)

    def _efetivar_aprovacao(self, solicitacao):
        """
        Libera o saldo e marca métricas (FTD).
        Agora dispara comissão se o promotor ganhar por DEPÓSITO.
        """
        usuario = solicitacao.usuario
        valor = solicitacao.valor
        
        # --- LÓGICA DE FTD (First Time Deposit) ---
        # Se for o primeiro depósito da vida dele, marcamos a data agora.
        if usuario.data_primeiro_deposito is None:
            usuario.data_primeiro_deposito = timezone.now()
            # (Futuro: Disparar evento de Pixel do Facebook/Google Ads aqui)
        
        # Aplica Bônus (Regra definida no model)
        bonus = usuario.aplicar_bonus_deposito(valor)
        
        # Atualiza Saldo
        saldo_anterior = usuario.saldo
        # Soma o valor depositado + bônus
        usuario.saldo += valor + bonus
        usuario.save()
        
        # ================= AQUI ENTRA A MUDANÇA (GATILHO) =================
        # Se o usuário tem um padrinho que ganha comissão por 'DEPOSITO', pagamos agora.
        # Passamos o valor ORIGINAL (sem bônus) como base de cálculo.
        usuario.processar_comissao(valor, 'DEPOSITO')
        # ==================================================================

        # Gera Extrato (Transação de Depósito)
        tx_deposito = Transacao.objects.create(
            usuario=usuario,
            tipo='DEPOSITO',
            valor=valor,
            # O saldo posterior aqui considera apenas o depósito para ficar claro no extrato
            # O bônus entra como uma transação separada logo abaixo
            saldo_anterior=saldo_anterior, 
            saldo_posterior=saldo_anterior + valor,
            descricao=f"Depósito Pix (ID: {solicitacao.id_externo})",
            origem_solicitacao=solicitacao 
        )
        
        # Gera Extrato (Transação de Bônus, se houver)
        if bonus > 0:
            Transacao.objects.create(
                usuario=usuario,
                tipo='BONUS',
                valor=bonus,
                saldo_anterior=tx_deposito.saldo_posterior,
                saldo_posterior=usuario.saldo, # Saldo final com bônus
                descricao="Bônus de Boas-vindas"
            )

        # Finaliza a solicitação
        solicitacao.status = 'APROVADO'
        solicitacao.data_aprovacao = timezone.now()
        solicitacao.save()

# --- 0. PAGINAÇÃO PADRÃO ---
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000

# --- 1. AUTH: REDEFINIÇÃO DE SENHA ---
class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Solicitar Reset de Senha",
        request={'application/json': {'properties': {'email': {'type': 'string'}}}},
        responses={200: OpenApiTypes.OBJECT}
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                # Na prática, envie um link para o frontend: https://seusite.com/reset/{uid}/{token}
                # Aqui simulamos o envio do token
                print(f"🔗 Link Reset (Simulado): /reset-password/{uid}/{token}/")
                return Response({"msg": "Se o email existir, enviamos um link."}, status=200)
            except CustomUser.DoesNotExist:
                # Retorna 200 mesmo se não existir para evitar enumeração de emails
                return Response({"msg": "Se o email existir, enviamos um link."}, status=200)
        return Response(serializer.errors, status=400)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        summary="Confirmar Nova Senha",
        parameters=[
            OpenApiParameter("uidb64", OpenApiTypes.STR, location=OpenApiParameter.PATH, description="ID do usuário codificado"),
            OpenApiParameter("token", OpenApiTypes.STR, location=OpenApiParameter.PATH, description="Token de verificação"),
        ],
        request={'application/json': {'properties': {'new_password': {'type': 'string'}}}},
        responses={200: OpenApiTypes.OBJECT}
    )
    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = CustomUser.objects.get(pk=uid)
                if default_token_generator.check_token(user, token):
                    user.set_password(serializer.validated_data['new_password'])
                    user.save()
                    return Response({"msg": "Senha alterada com sucesso!"})
                return Response({"erro": "Token inválido ou expirado"}, status=400)
            except:
                return Response({"erro": "Link inválido"}, status=400)
        return Response(serializer.errors, status=400)

# --- 2. BACKOFFICE: GESTÃO DE PAGAMENTOS (Admin) ---
# --- 2. BACKOFFICE: GESTÃO DE PAGAMENTOS (Admin) ---
class BackofficeSolicitacaoViewSet(viewsets.ModelViewSet):
    """
    Endpoint completo para Admin gerenciar Depósitos e Saques.
    Inclui: Listagem, Filtros, Busca, Aprovação, Detalhes e Exportação.
    """
    queryset = SolicitacaoPagamento.objects.all().select_related('usuario').order_by('-criado_em')
    serializer_class = SolicitacaoPagamentoAdminSerializer
    permission_classes = [IsAdminUser] # Apenas Staff
    pagination_class = StandardResultsSetPagination
    
    # Filtros Poderosos
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'tipo', 'usuario__conta_suspeita'] # Filtro exato
    search_fields = ['usuario__nome_completo', 'usuario__email', 'usuario__cpf_cnpj', 'id_externo'] # Busca Texto
    ordering_fields = ['valor', 'criado_em', 'risco_score']

    # Ação: Analisar (Aprovar/Recusar)
    @extend_schema(
        summary="Analisar Solicitação",
        description="Aprova ou recusa um saque/depósito. Requer motivo se recusado.",
        request=AnaliseSolicitacaoSerializer,
        responses={200: OpenApiTypes.OBJECT}
    )
    @action(detail=True, methods=['post'])
    def analisar(self, request, pk=None):
        solicitacao = self.get_object()
        serializer = AnaliseSolicitacaoSerializer(data=request.data)
        if serializer.is_valid():
            acao = serializer.validated_data['acao']
            motivo = serializer.validated_data.get('motivo', '')
            
            if solicitacao.status != 'EM_ANALISE' and solicitacao.status != 'PENDENTE':
                return Response({"erro": "Solicitação não está pendente"}, status=400)

            if acao == 'APROVAR':
                if solicitacao.tipo == 'SAQUE':
                    # Futuro: Integração SkalePayService.solicitar_saque_pix(...)
                    solicitacao.status = 'APROVADO' 
                else:
                    # Depósito manual
                    usuario = solicitacao.usuario
                    usuario.saldo += solicitacao.valor
                    usuario.save()
                    solicitacao.status = 'APROVADO'
                
                solicitacao.data_aprovacao = timezone.now()
                solicitacao.aprovado_por = request.user
                solicitacao.save()
                return Response({"msg": "Aprovado com sucesso"})

            elif acao == 'RECUSAR':
                solicitacao.status = 'RECUSADO'
                solicitacao.analise_motivo = motivo
                solicitacao.reprovado_por = request.user
                solicitacao.data_reprovacao = timezone.now()
                
                # Se for saque, estorna o saldo
                if solicitacao.tipo == 'SAQUE':
                    solicitacao.usuario.saldo += solicitacao.valor
                    solicitacao.usuario.save()
                
                solicitacao.save()
                return Response({"msg": "Recusado e saldo estornado (se saque)."})

        return Response(serializer.errors, status=400)

    # Ação: Download CSV
    @extend_schema(
        summary="Baixar CSV",
        description="Gera download do relatório com os filtros aplicados.",
        responses={200: OpenApiTypes.BINARY}
    )
    @action(detail=False, methods=['get'])
    def download_csv(self, request):
        # Aplica os mesmos filtros da tela antes de baixar
        queryset = self.filter_queryset(self.get_queryset())
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="relatorio_financeiro_{timezone.now().date()}.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Data', 'Usuário', 'CPF', 'Tipo', 'Valor', 'Status', 'Risco'])

        for item in queryset:
            writer.writerow([
                item.id, 
                item.criado_em.strftime('%d/%m/%Y %H:%M'),
                item.usuario.nome_completo,
                item.usuario.cpf_cnpj,
                item.tipo,
                item.valor,
                item.status,
                item.risco_score
            ])
        return response

# --- 3. RISCO & COMPLIANCE (Relatórios Especiais) ---
class RiscoComplianceViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]
    @extend_schema(summary="Listar Multi-Contas por IP", responses={200: OpenApiTypes.OBJECT})
    @action(detail=False, methods=['get'])
    def multiconstas_ip(self, request):
        """Lista IPs com mais de 1 cadastro"""
        qs = CustomUser.objects.values('ultimo_ip').annotate(
            total_contas=Count('id')
        ).filter(total_contas__gt=1).order_by('-total_contas')
        
        # Paginação manual para ViewSet simples
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        
        resultado = []
        for item in page:
            users = CustomUser.objects.filter(ultimo_ip=item['ultimo_ip']).values_list('email', flat=True)
            resultado.append({
                "ip": item['ultimo_ip'],
                "total": item['total_contas'],
                "usuarios": list(users)
            })
            
        return paginator.get_paginated_response(resultado)

    @extend_schema(summary="Padrão Depósito-Saque", responses={200: OpenApiTypes.OBJECT})
    @action(detail=False, methods=['get'])
    def padrao_deposito_saque(self, request):
        """Lista usuários que depositaram e sacaram rápido (GAP 1)"""
        suspeitos = []
        saques_recentes = Transacao.objects.filter(
            tipo='SAQUE', 
            data__gte=timezone.now() - timezone.timedelta(days=7)
        ).select_related('usuario')

        for saque in saques_recentes:
            deposito_recente = Transacao.objects.filter(
                usuario=saque.usuario,
                tipo='DEPOSITO',
                data__lt=saque.data,
                data__gte=saque.data - timezone.timedelta(hours=2)
            ).exists()
            
            if deposito_recente:
                suspeitos.append({
                    "usuario": saque.usuario.email,
                    "data_saque": saque.data,
                    "valor_saque": saque.valor,
                    "motivo": "Saque < 2h após depósito (Lavagem?)"
                })
        
        # --- [CORREÇÃO] APLICAÇÃO DA PAGINAÇÃO ---
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(suspeitos, request)
        return paginator.get_paginated_response(page)
    @extend_schema(summary="Abuso de Bônus", responses={200: OpenApiTypes.OBJECT})
    @action(detail=False, methods=['get'])
    def padrao_bonus_saque(self, request):
        """
        Lista usuários que receberam bônus e tentaram sacar logo depois.
        Filtra: Transação 'BONUS' seguida de 'SAQUE' (Tentativa ou Sucesso) em < 24h.
        """
        suspeitos = []
        saques = Transacao.objects.filter(
            tipo='SAQUE',
            data__gte=timezone.now() - timezone.timedelta(days=7)
        ).select_related('usuario')

        for saque in saques:
            teve_bonus = Transacao.objects.filter(
                usuario=saque.usuario,
                tipo='BONUS',
                data__lt=saque.data,
                data__gte=saque.data - timezone.timedelta(hours=24)
            ).exists()
            
            if teve_bonus:
                suspeitos.append({
                    "usuario": saque.usuario.email,
                    "data_bonus": "Detectado < 24h antes",
                    "data_saque": saque.data,
                    "valor_saque": saque.valor,
                    "risco": "Abuso de Bônus (Saque rápido após bônus)"
                })
        
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(suspeitos, request)
        return paginator.get_paginated_response(page)

# --- 4. ÁREA DO USUÁRIO (Meus Dados) ---

class HistoricoUsuarioView(viewsets.ReadOnlyModelViewSet):
    """
    Histórico financeiro do próprio usuário logado.
    """
    serializer_class = SolicitacaoPagamentoAdminSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    # --- ADICIONADO AGORA: FILTROS PARA O USUÁRIO ---
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tipo', 'status'] # Usuário pode filtrar por Saque/Deposito e Status
    ordering_fields = ['valor', 'criado_em']
    ordering = ['-criado_em'] # Padrão: mais recentes primeiro
    # ------------------------------------------------

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SolicitacaoPagamento.objects.none()
        return SolicitacaoPagamento.objects.filter(usuario=self.request.user).order_by('-criado_em')

# --- 5. OPERACIONAL (Listas de Modalidades e Picos) ---
class RelatoriosOperacionaisView(APIView):
    permission_classes = [IsAdminUser]
    @extend_schema(summary="Relatório Operacional", responses={200: OpenApiTypes.OBJECT}) 
    def get(self, request):
        # Filtro de data
        data_str = request.query_params.get('data', str(timezone.localdate()))
        try:
            data_ref = timezone.datetime.strptime(data_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({"erro": "Formato de data inválido. Use AAAA-MM-DD"}, status=400)

        # Dados existentes no MetricasDiarias
        metrica = MetricasDiarias.objects.filter(data=data_ref).first()
        
        if not metrica:
            return Response({"aviso": "Sem métricas processadas para esta data."}, status=404)

        return Response({
            "data": data_str,
            "performance_modalidades": metrica.performance_modalidades, # Lista de modalidades
            "horarios_pico": metrica.mapa_calor_horas, # Horário e Volume
            "volumes_pendentes": {
                "depositos": SolicitacaoPagamento.objects.filter(status='PENDENTE', tipo='DEPOSITO').count(),
                "saques": SolicitacaoPagamento.objects.filter(status='PENDENTE', tipo='SAQUE').count(),
            }
        })
    
class RelatorioFinanceiroView(APIView):
    permission_classes = [IsAdminUser] # Apenas Admin/Staff
    @extend_schema(summary="Relatório Transações", responses={200: SolicitacaoPagamentoAdminSerializer(many=True)}) 
    def get(self, request):
        # 1. Filtros de Data
        data_inicio = request.query_params.get('inicio')
        data_fim = request.query_params.get('fim')
        tipo_filtro = request.query_params.get('tipo') # 'DEPOSITO', 'SAQUE', 'APOSTA', 'COMISSAO'

        # 2. Base da Query
        queryset = Transacao.objects.select_related('usuario').all().order_by('-data')

        if data_inicio:
            queryset = queryset.filter(data__date__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data__date__lte=data_fim)
        if tipo_filtro:
            queryset = queryset.filter(tipo=tipo_filtro)

        # 3. Preparar o CSV (Nativo do Python, super rápido)
        response = HttpResponse(content_type='text/csv')
        filename = f"relatorio_financeiro_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        
        # Cabeçalho do Excel
        writer.writerow(['ID', 'Data/Hora', 'Usuário (CPF)', 'Tipo', 'Valor (R$)', 'Saldo Anterior', 'Saldo Final', 'Descrição'])

        # Dados
        for item in queryset:
            writer.writerow([
                item.id,
                item.data.strftime('%d/%m/%Y %H:%M:%S'),
                f"{item.usuario.nome_completo} ({item.usuario.cpf_cnpj})",
                item.get_tipo_display(),
                str(item.valor).replace('.', ','), # Formato Brasileiro
                str(item.saldo_anterior).replace('.', ','),
                str(item.saldo_posterior).replace('.', ','),
                item.descricao
            ])

        return response

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Perfil do Usuário",
        description="Retorna os dados do usuário logado (Nome, Saldo, Email).",
        responses={200: UserSerializer}
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
