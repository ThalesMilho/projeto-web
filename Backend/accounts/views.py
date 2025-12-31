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
from .models import Transacao, CustomUser
from games.models import Aposta


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
    Retorna métricas consolidadas para o Painel Administrativo.
    Apenas Administradores podem ver.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        hoje = timezone.localdate()

        # 1. Resumo Geral (Vida inteira da banca)
        total_apostado = Aposta.objects.aggregate(Sum('valor'))['valor__sum'] or 0
        total_pago = Aposta.objects.filter(ganhou=True).aggregate(Sum('valor_premio'))['valor_premio__sum'] or 0
        house_edge = total_apostado - total_pago # Lucro Bruto
        
        # 2. Movimentação do Dia (Hoje)
        apostas_hoje = Aposta.objects.filter(criado_em__date=hoje).aggregate(Sum('valor'))['valor__sum'] or 0
        premios_hoje = Aposta.objects.filter(ganhou=True, criado_em__date=hoje).aggregate(Sum('valor_premio'))['valor_premio__sum'] or 0
        lucro_hoje = apostas_hoje - premios_hoje

        # 3. Métricas de Usuários
        total_users = CustomUser.objects.count()
        novos_users_hoje = CustomUser.objects.filter(date_joined__date=hoje).count()

        # 4. Cash Flow (Entradas e Saídas Reais - Depósitos/Saques)
        depositos = Transacao.objects.filter(tipo='DEPOSITO').aggregate(Sum('valor'))['valor__sum'] or 0
        saques = Transacao.objects.filter(tipo='SAQUE').aggregate(Sum('valor'))['valor__sum'] or 0

        return Response({
            "hoje": {
                "faturamento": apostas_hoje,
                "premios_pagos": premios_hoje,
                "lucro_liquido": lucro_hoje,
                "novos_usuarios": novos_users_hoje
            },
            "acumulado": {
                "total_apostado": total_apostado,
                "total_pago": total_pago,
                "lucro_operacional": house_edge,
                "margem_lucro": f"{((house_edge/total_apostado)*100):.1f}%" if total_apostado > 0 else "0%"
            },
            "tesouraria": {
                "total_depositado": depositos,
                "total_sacado": saques,
                "saldo_em_conta": depositos - saques
            },
            "usuarios_ativos": total_users
        })
class SimularDepositoView(APIView):
    """
    Simula um Webhook de Pagamento (Admin Only).
    Aplica regra de Bônus: 100% no 1º depósito (Teto R$ 100) e Rollover 2x.
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        user_id = request.data.get('user_id')
        valor = Decimal(str(request.data.get('valor')))

        try:
            with transaction.atomic():
                usuario = CustomUser.objects.select_for_update().get(id=user_id)
                
                # --- Lógica do Bônus ---
                bonus =usuario.aplicar_bonus_deposito(valor)
                saldo_anterior = usuario.saldo
                usuario.saldo += valor + bonus
                usuario.save()
                Transacao.objects.create(
                    usuario=usuario,
                    tipo='DEPOSITO',
                    valor=valor,
                    saldo_anterior=saldo_anterior,
                    saldo_posterior=usuario.saldo,
                    descricao=f"Depósito Simulado via Webhook. Bônus aplicado: R$ {bonus:.2f}"
                )

                if bonus > 0 :
                    Transacao.objects.create(
                        usuario=usuario,
                        tipo='BONUS',
                        valor=bonus,
                        saldo_anterior=usuario.saldo + valor,
                        saldo_posterior=usuario.saldo,
                        descricao="Bônus de Boas-Vindas(100%)"
                    )
            return Response({
                "mensagem": "Depósito simulado com sucesso!",
                "saldo_atual": usuario.saldo,
                "bonus_aplicado": bonus,
                "meta_rollover": usuario.meta_rollover
            })

        except Exception as e:
            return Response({"erro": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class SolicitarSaqueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        valor = Decimal(str(request.data.get('valor')))
        usuario = request.user

        try:
            with transaction.atomic():
                # Trava o usuário para evitar saque duplo
                user_travado = CustomUser.objects.select_for_update().get(id=usuario.id)

                # 1. Verifica Saldo
                if user_travado.saldo < valor:
                    return Response({"erro": "Saldo insuficiente."}, status=status.HTTP_400_BAD_REQUEST)

                # 2. Verifica ROLLOVER (A Proteção do Bônus)
                if not user_travado.pode_sacar():
                    falta = user_travado.quanto_falta_rollover()
                    return Response({
                        "erro": "Saque bloqueado por regras de Bônus.",
                        "detalhe": f"Você precisa apostar mais R$ {falta:.2f} antes de sacar."
                    }, status=status.HTTP_400_BAD_REQUEST)

                # 3. Processa o Saque
                saldo_anterior = user_travado.saldo
                user_travado.saldo -= valor
                user_travado.save()

                Transacao.objects.create(
                    usuario=user_travado,
                    tipo='SAQUE',
                    valor=valor,
                    saldo_anterior=saldo_anterior,
                    saldo_posterior=user_travado.saldo,
                    descricao="Solicitação de Saque PIX"
                )

            return Response({"mensagem": "Saque realizado com sucesso!", "novo_saldo": user_travado.saldo})

        except Exception as e:
            return Response({"erro": str(e)}, status=status.HTTP_400_BAD_REQUEST)