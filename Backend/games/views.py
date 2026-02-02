from rest_framework import viewsets, mixins, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.db import transaction, DatabaseError, IntegrityError
from django.db.models import F
from decimal import Decimal, ROUND_DOWN
import logging
from django.shortcuts import get_object_or_404, render

from .models import Sorteio, Aposta, ParametrosDoJogo

from drf_spectacular.utils import extend_schema, OpenApiTypes

# Imports de outros apps e utilitários
from accounts.models import Transacao
from .utils import descobrir_bicho
from decimal import Decimal
import math
from collections import Counter

# Imports dos Serializers
from .serializer import SorteioSerializer, CriarApostaSerializer, ApostaDetalheSerializer

logger = logging.getLogger(__name__)


# --- VIEWS DE LEITURA (GET - Públicas) ---

class BichosView(APIView):
    permission_classes = [permissions.AllowAny]
    @extend_schema(summary="Lista de Bichos", responses={200: OpenApiTypes.OBJECT}) 
    def get(self, request):
        bichos = [
            {"numero": 1, "nome": "Avestruz", "dezenas": "01, 02, 03, 04"},
            {"numero": 2, "nome": "Águia", "dezenas": "05, 06, 07, 08"},
            {"numero": 3, "nome": "Burro", "dezenas": "09, 10, 11, 12"},
            {"numero": 4, "nome": "Borboleta", "dezenas": "13, 14, 15, 16"},
            {"numero": 5, "nome": "Cachorro", "dezenas": "17, 18, 19, 20"},
            {"numero": 6, "nome": "Cabra", "dezenas": "21, 22, 23, 24"},
            {"numero": 7, "nome": "Carneiro", "dezenas": "25, 26, 27, 28"},
            {"numero": 8, "nome": "Camelo", "dezenas": "29, 30, 31, 32"},
            {"numero": 9, "nome": "Cobra", "dezenas": "33, 34, 35, 36"},
            {"numero": 10, "nome": "Coelho", "dezenas": "37, 38, 39, 40"},
            {"numero": 11, "nome": "Cavalo", "dezenas": "41, 42, 43, 44"},
            {"numero": 12, "nome": "Elefante", "dezenas": "45, 46, 47, 48"},
            {"numero": 13, "nome": "Galo", "dezenas": "49, 50, 51, 52"},
            {"numero": 14, "nome": "Gato", "dezenas": "53, 54, 55, 56"},
            {"numero": 15, "nome": "Jacaré", "dezenas": "57, 58, 59, 60"},
            {"numero": 16, "nome": "Leão", "dezenas": "61, 62, 63, 64"},
            {"numero": 17, "nome": "Macaco", "dezenas": "65, 66, 67, 68"},
            {"numero": 18, "nome": "Porco", "dezenas": "69, 70, 71, 72"},
            {"numero": 19, "nome": "Pavão", "dezenas": "73, 74, 75, 76"},
            {"numero": 20, "nome": "Peru", "dezenas": "77, 78, 79, 80"},
            {"numero": 21, "nome": "Touro", "dezenas": "81, 82, 83, 84"},
            {"numero": 22, "nome": "Tigre", "dezenas": "85, 86, 87, 88"},
            {"numero": 23, "nome": "Urso", "dezenas": "89, 90, 91, 92"},
            {"numero": 24, "nome": "Veado", "dezenas": "93, 94, 95, 96"},
            {"numero": 25, "nome": "Vaca", "dezenas": "97, 98, 99, 00"},
        ]
        return Response(bichos, status=status.HTTP_200_OK)

class CotacaoView(APIView):
    """
    Retorna as modalidades de jogo baseadas no padrão de mercado (Prints enviados).
    """
    permission_classes = [permissions.AllowAny]
    @extend_schema(summary="Cotações Atuais", responses={200: OpenApiTypes.OBJECT}) 
    def get(self, request):
        config = ParametrosDoJogo.load()

        # Função auxiliar: Pega o valor do banco, se não existir, usa o padrão (evita o crash)
        def val(campo, padrao):
            valor = getattr(config, campo, padrao)
            return float(valor) if valor is not None else padrao

        # Sua lista original, agora protegida
        lista_jb = [
            {"modalidade": "M", "nome": "MILHAR", "fator": val('cotacao_milhar', 4000.0)}, 
            {"modalidade": "C", "nome": "CENTENA", "fator": val('cotacao_centena', 600.0)}, 
            {"modalidade": "D", "nome": "DEZENA", "fator": val('cotacao_dezena', 60.0)},  
            {"modalidade": "U", "nome": "UNIDADE", "fator": 8.0},         
            {"modalidade": "G", "nome": "GRUPO", "fator": val('cotacao_grupo', 18.0)},    

            # Variações (Usando valores padrão pois não estão no Model ainda)
            {"modalidade": "MC", "nome": "MILHAR E CENTENA (MC)", "fator": 2000.0}, 
            {"modalidade": "MINV", "nome": "MILHAR INVERTIDA", "fator": val('cotacao_milhar_invertida', 400.0)},
            {"modalidade": "CINV", "nome": "CENTENA INVERTIDA", "fator": val('cotacao_centena_invertida', 100.0)},
            
            # Hardcoded (Mantidos)
            {"modalidade": "C_ESQ", "nome": "CENTENA ESQUERDA", "fator": 600.0},
            {"modalidade": "C_INV_ESQ", "nome": "CENTENA INV ESQ", "fator": 100.0},
            {"modalidade": "C_3X", "nome": "CENTENA 3X", "fator": 200.0}, 

            {"modalidade": "DD", "nome": "DUQUE DE DEZENA", "fator": val('cotacao_duque_dezena', 300.0)},
            {"modalidade": "TDS", "nome": "TERNO DEZ SECO", "fator": 10000.0},
            {"modalidade": "TD", "nome": "TERNO DE DEZENA", "fator": val('cotacao_terno_dezena', 5000.0)},

            {"modalidade": "DG", "nome": "DUQUE DE GRUPO", "fator": 200.0},    
            {"modalidade": "TG", "nome": "TERNO DE GRUPO", "fator": 1500.0},  
            {"modalidade": "QG", "nome": "QUADRA DE GRUPO", "fator": 1000.0},  

            {"modalidade": "QNG", "nome": "QUINA GP 8/5", "fator": 1000.0},
            {"modalidade": "QNG_ESQ", "nome": "QUINA GP 8/5 ESQ", "fator": 1000.0},
            {"modalidade": "QNG_MEIO", "nome": "QUINA GP 8/5 MEIO", "fator": 1000.0},

            {"modalidade": "SENA", "nome": "SENA GP 10/6", "fator": 1000.0},
            {"modalidade": "SENA_ESQ", "nome": "SENA GP 10/6 ESQ", "fator": 1000.0},
            {"modalidade": "SENA_MEIO", "nome": "SENA GP 10/6 MEIO", "fator": 1000.0},

            {"modalidade": "PV", "nome": "PASSE VAI", "fator": val('cotacao_passe_vai', 90.0)},         
            {"modalidade": "PVV", "nome": "PASSE VAI VEM", "fator": val('cotacao_passe_vai_vem', 45.0)},  
            {"modalidade": "PALP", "nome": "PALPITÃO", "fator": 800.0},       
        ]

        # Retorna TUDO que o front precisa num objeto só
        return Response({
            "lista_jb": lista_jb,
            "quininha": config.cotacao_quininha,
            "seninha": config.cotacao_seninha,
            "lotinha": config.cotacao_lotinha
        })

class SorteiosAbertosView(APIView):
    permission_classes = [permissions.AllowAny]
    @extend_schema(summary="Sorteios Abertos", responses={200: OpenApiTypes.OBJECT}) 
    def get(self, request):
        hoje = timezone.localdate()
        sorteios = Sorteio.objects.filter(
            data__gte=hoje, 
            fechado=False
        ).order_by('data', 'id') 

        serializer = SorteioSerializer(sorteios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)    

class QuininhaView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        data = {
            "nome_jogo": "Quininha",
            "descricao": "Neste jogo, você aposta em dezenas em 5 faixas de premiação.",
            "regras": [
                {"tipo": "Unidade", "premio": "R$ 4,00 para 1"},
                {"tipo": "Dezena", "premio": "R$ 40,00 para 1"},
                {"tipo": "Centena", "premio": "R$ 400,00 para 1"},
                {"tipo": "Milhar", "premio": "R$ 4.000,00 para 1"},
                {"tipo": "Quininha", "premio": "R$ 200,00 para 1"},
            ],
            "como_jogar": "Escolha suas dezenas e faça sua aposta. Quanto mais você apostar, maiores são suas chances de ganhar!",
        }
        return Response(data, status=status.HTTP_200_OK)

class SeninhaView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        data = {
            "nome_jogo": "Seninha",
            "descricao": "O dobro da emoção da Quininha, com 10 faixas de premiação.",
            "regras": [
                {"tipo": "Unidade", "premio": "R$ 3,00 para 1"},
                {"tipo": "Dezena", "premio": "R$ 30,00 para 1"},
                {"tipo": "Centena", "premio": "R$ 300,00 para 1"},
                {"tipo": "Milhar", "premio": "R$ 3.000,00 para 1"},
                {"tipo": "Quininha", "premio": "R$ 150,00 para 1"},
                {"tipo": "Seninha", "premio": "R$ 1.000,00 para 1"},
                {"tipo": "Prêmios do 1º ao 10º", "premio": "R$ 2.000,00 para 1"},
            ],
            "como_jogar": "Escolha suas dezenas e faça sua aposta. Quanto mais você apostar, maiores são suas chances de ganhar!",
        }
        return Response(data, status=status.HTTP_200_OK)

class LotinhaView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        data = {
            "nome_jogo": "Lotinha",
            "descricao": "Jogo especial com regras diferenciadas, focando em grupos e combinações.",
            "regras": [
                {"tipo": "Grupo 1", "premio": "R$ 20,00 para 1"},
                {"tipo": "Grupo 2", "premio": "R$ 10,00 para 1"},
                {"tipo": "Dupla de Grupo", "premio": "R$ 300,00 para 1"},
                {"tipo": "Terno de Grupo", "premio": "R$ 1.500,00 para 1"},
            ], 
            "como_jogar": "Escolha suas dezenas e faça sua aposta. Quanto mais você apostar, maiores são suas chances de ganhar!",
        }
        return Response(data, status=status.HTTP_200_OK)


# --- VIEWSETS DE AÇÃO (Protegidos) ---

class ApuracaoAPIView(APIView): 
    """
    Endpoint para disparar a apuração via API (alternativa ao botão do Admin).
    """
    permission_classes = [permissions.IsAdminUser]
    @extend_schema(
        summary="Rodar Apuração Manual",
        description="Força o sistema a verificar vencedores para um sorteio específico.",
        request={'application/json': {'properties': {'sorteio_id': {'type': 'integer'}}}},
        responses={200: OpenApiTypes.OBJECT}
    )
    def post(self, request, pk):
        sorteio = get_object_or_404(Sorteio, pk=pk)
        
        # Reutiliza a lógica robusta que já criamos no Model (DRY)
        if hasattr(sorteio, 'apurar_resultados'):
            sucesso = sorteio.apurar_resultados()
            if sucesso:
                return Response({"mensagem": "Apuração concluída com sucesso!"})
            else:
                return Response({"erro": "Não foi possível apurar. Verifique se os prêmios estão cadastrados."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"erro": "Método de apuração não encontrado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- VIEW VISUAL (HTML) ---

def comprovante_view(request, pk):
    """
    View simples para renderizar o ticket de impressão.
    """
    # Segurança: Garante que o usuário só imprima o SEU bilhete
    aposta = get_object_or_404(Aposta, pk=pk, usuario=request.user)
    return render(request, 'games/ticket.html', {'aposta': aposta})

class ApostaViewSet(mixins.CreateModelMixin, 
                    mixins.ListModelMixin, 
                    mixins.RetrieveModelMixin, 
                    viewsets.GenericViewSet):
    """
    ViewSet que gerencia as Apostas (Cria e Lista).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Aposta.objects.none()
            
        return Aposta.objects.filter(usuario=self.request.user).order_by('-criado_em')

    def get_serializer_class(self):
        if self.action == 'create':
            return CriarApostaSerializer
        return ApostaDetalheSerializer

    def create(self, request, *args, **kwargs):
        # --- NOVO: VERIFICAÇÃO DO KILL SWITCH ---
        # Antes de qualquer coisa, checa se o sistema está ligado no Admin
        config = ParametrosDoJogo.load()
        if not config.ativa_apostas:
            return Response(
                {"erro": "O sistema de apostas está temporariamente suspenso."}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        # ----------------------------------------

        # Validação inicial dos dados
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        dados = serializer.validated_data
        user = request.user
        valor_aposta = dados['valor']
        sorteio_alvo = dados['sorteio']

        # 1. Anti-spam (evita duplo clique)
        if Aposta.objects.filter(
            usuario=user, 
            sorteio=sorteio_alvo, 
            valor=valor_aposta, 
            palpite=dados['palpite'], 
            criado_em__gte=timezone.now() - timezone.timedelta(seconds=5)
        ).exists():
            return Response({"erro": "Aposta duplicada. Aguarde..."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Lock order: Sempre Sorteio -> Usuario (evita deadlocks)
                sorteio_travado = Sorteio.objects.select_for_update().get(pk=sorteio_alvo.pk)
                user_travado = type(user).objects.select_for_update().get(pk=user.pk)

                # 3. Verifica Saldo
                if user_travado.saldo < valor_aposta:
                    return Response({"erro": "Saldo insuficiente."}, status=status.HTTP_400_BAD_REQUEST)

                # 4. Verifica se o sorteio ainda está aberto
                if sorteio_travado.fechado:
                    return Response({"erro": "Sorteio fechado."}, status=status.HTTP_400_BAD_REQUEST)

                # 5. Debita o valor
                saldo_anterior = user_travado.saldo
                user_travado.saldo = F('saldo') - valor_aposta
                user_travado.save()
                user_travado.refresh_from_db()

                # --- 6. LÓGICA DE CAMBISTA (Auto-comissão) ---
                comissao_valor = Decimal('0.00')
                if user_travado.tipo_usuario == 'AFILIADO' and user_travado.comissao_percentual > 0:
                    raw_comissao = (valor_aposta * (user_travado.comissao_percentual / Decimal('100')))
                    CENTS = Decimal('0.01')
                    comissao_valor = raw_comissao.quantize(CENTS, rounding=ROUND_DOWN)

                    # Credita comissão no saldo do próprio cambista
                    prev_saldo = user_travado.saldo
                    user_travado.saldo = F('saldo') + comissao_valor
                    user_travado.save()
                    user_travado.refresh_from_db()

                    # Gera o LOG da comissão do cambista (Trazido para o lugar certo!)
                    Transacao.objects.create(
                        usuario=user_travado,
                        tipo='COMISSAO',
                        valor=comissao_valor,
                        saldo_anterior=prev_saldo,
                        saldo_posterior=user_travado.saldo,
                        descricao=f"Comissão sobre aposta - {dados['palpite']} ({dados['tipo_jogo']})"
                    )

                # --- 7. SALVA A APOSTA ORIGINAL ---
                aposta = serializer.save(usuario=user_travado, comissao_gerada=comissao_valor)

                if aposta.comissao_gerada != comissao_valor:
                    raise ValueError("Serializer ignored 'comissao_gerada' during save.")

                # --- 8. GATILHO DE AFILIADOS (Promotores/Padrinhos) ---
                # Fica FORA do if do cambista, para valer para todo mundo
                user_travado.processar_comissao(valor_aposta, 'APOSTA')

                # --- 9. PROMOÇÃO MILHAR BRINDE ---
                # Carrega config aqui fora para garantir que existe
                config = ParametrosDoJogo.load()
                
                if config.milhar_brinde_ativa and valor_aposta >= config.valor_minimo_para_brinde:
                    import random
                    # Gera um número aleatório de 0000 a 9999
                    palpite_brinde = f"{random.randint(0, 9999):04d}"
                    
                    # Cria a aposta extra (Gratuita)
                    Aposta.objects.create(
                        usuario=user_travado,
                        sorteio=sorteio_travado, 
                        tipo_jogo='MB',          
                        valor=Decimal('0.00'),   
                        palpite=palpite_brinde,
                        comissao_gerada=Decimal('0.00')
                    )

                # --- 10. CRIA EXTRATO DA APOSTA ---
                Transacao.objects.create(
                    usuario=user_travado,
                    tipo='APOSTA',
                    valor=valor_aposta,
                    saldo_anterior=saldo_anterior,
                    saldo_posterior=user_travado.saldo, # Saldo final já descontado a aposta (e somado a comissão se for cambista)
                    descricao=f"Jogo: {aposta.get_tipo_jogo_display()} - {aposta.palpite}"
                )

                read_serializer = ApostaDetalheSerializer(aposta)
                return Response(read_serializer.data, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            logger.warning("Integrity error creating aposta: %s", e)
            return Response({"erro": "Conflito ao criar aposta."}, status=status.HTTP_409_CONFLICT)
        except ValueError as e:
            logger.error("Validation/integrity error while creating aposta: %s", e, exc_info=True)
            return Response({"erro": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.critical("Unexpected error creating aposta", exc_info=True)
            return Response({"erro": "Erro interno do servidor."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)