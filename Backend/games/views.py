from rest_framework import viewsets, mixins, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.db import transaction, DatabaseError
from django.db.models import F
from django.shortcuts import get_object_or_404, render

# --- AQUI ESTAVA FALTANDO: Importação dos seus Models ---
from .models import Sorteio, Aposta, ParametrosDoJogo

# Imports de outros apps e utilitários
from accounts.models import Transacao
from .utils import descobrir_bicho
from decimal import Decimal
import math
from collections import Counter

# Imports dos Serializers
from .serializer import SorteioSerializer, CriarApostaSerializer, ApostaDetalheSerializer


# --- VIEWS DE LEITURA (GET - Públicas) ---

class BichosView(APIView):
    permission_classes = [permissions.AllowAny]

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
        bichos = [{"numero": i, "nome": "Bicho Exemplo"} for i in range(1, 26)]
        return Response(bichos, status=status.HTTP_200_OK)

class CotacaoView(APIView):
    """
    Retorna as modalidades de jogo baseadas no padrão de mercado (Prints enviados).
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Carrega configurações dinâmicas para os jogos base
        config = ParametrosDoJogo.load()
        
        cotacoes = [
            # --- 1. MODALIDADES BÁSICAS (Controladas pelo Admin) ---
            {"modalidade": "M", "nome": "MILHAR", "fator": float(config.cotacao_milhar)}, 
            {"modalidade": "C", "nome": "CENTENA", "fator": float(config.cotacao_centena)}, 
            {"modalidade": "D", "nome": "DEZENA", "fator": float(config.cotacao_dezena)},  
            {"modalidade": "U", "nome": "UNIDADE", "fator": 8.0},         
            {"modalidade": "G", "nome": "GRUPO", "fator": float(config.cotacao_grupo)},    

            # --- 2. VARIAÇÕES DE MILHAR E CENTENA ---
            {"modalidade": "MC", "nome": "MILHAR E CENTENA (MC)", "fator": float(config.cotacao_milhar_centena)},
            {"modalidade": "MINV", "nome": "MILHAR INVERTIDA", "fator": 8000.0},
            {"modalidade": "CINV", "nome": "CENTENA INVERTIDA", "fator": 800.0},
            
            # Variações de Posição
            {"modalidade": "C_ESQ", "nome": "CENTENA ESQUERDA", "fator": 800.0},
            {"modalidade": "C_INV_ESQ", "nome": "CENTENA INV ESQ", "fator": 800.0},
            {"modalidade": "C_3X", "nome": "CENTENA 3X", "fator": 200.0}, # Estimado, pois não aparece valor no print

            # --- 3. COMBINAÇÕES DE DEZENA ---
            {"modalidade": "DD", "nome": "DUQUE DE DEZENA", "fator": 300.0},
            {"modalidade": "TDS", "nome": "TERNO DEZ SECO", "fator": 10000.0},
            {"modalidade": "TD", "nome": "TERNO DE DEZENA", "fator": 5000.0},

            # --- 4. COMBINAÇÕES DE GRUPO (GP) ---
            {"modalidade": "DG", "nome": "DUQUE DE GRUPO", "fator": 200.0},    
            {"modalidade": "TG", "nome": "TERNO DE GRUPO", "fator": 1500.0},  
            {"modalidade": "QG", "nome": "QUADRA DE GRUPO", "fator": 1000.0},  

            # --- 5. QUINA DE GRUPO  ---
            {"modalidade": "QNG", "nome": "QUINA GP 8/5", "fator": 1000.0},
            {"modalidade": "QNG_ESQ", "nome": "QUINA GP 8/5 ESQ", "fator": 1000.0},
            {"modalidade": "QNG_MEIO", "nome": "QUINA GP 8/5 MEIO", "fator": 1000.0},

            # --- 6. SENA DE GRUPO ---
            {"modalidade": "SENA", "nome": "SENA GP 10/6", "fator": 1000.0},
            {"modalidade": "SENA_ESQ", "nome": "SENA GP 10/6 ESQ", "fator": 1000.0},
            {"modalidade": "SENA_MEIO", "nome": "SENA GP 10/6 MEIO", "fator": 1000.0},

            # --- 7. PASSES E ESPECIAIS ---
            {"modalidade": "PV", "nome": "PASSE VAI", "fator": 90.0},         
            {"modalidade": "PVV", "nome": "PASSE VAI VEM", "fator": 45.0},  
            {"modalidade": "PALP", "nome": "PALPITÃO", "fator": 800.0},       
        ]
        return Response(cotacoes, status=status.HTTP_200_OK)

class SorteiosAbertosView(APIView):
    permission_classes = [permissions.AllowAny]

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
        # Usuário só vê as próprias apostas
        return Aposta.objects.filter(usuario=self.request.user).order_by('-criado_em')

    def get_serializer_class(self):
        if self.action == 'create':
            return CriarApostaSerializer
        return ApostaDetalheSerializer

    def create(self, request, *args, **kwargs):
        # Validação inicial dos dados
        serializer = self.get_serializer(data=request.data)
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
                # 2. Trava a conta do usuário (Select For Update)
                user_travado = type(user).objects.select_for_update().get(pk=user.pk)

                # 3. Verifica Saldo
                if user_travado.saldo < valor_aposta:
                    return Response({"erro": "Saldo insuficiente."}, status=status.HTTP_400_BAD_REQUEST)

                # 4. Verifica se o sorteio ainda está aberto
                if sorteio_alvo.fechado:
                    return Response({"erro": "Sorteio fechado."}, status=status.HTTP_400_BAD_REQUEST)

                # 5. Debita o valor
                user_travado.saldo = F('saldo') - valor_aposta
                user_travado.save()
                user_travado.refresh_from_db()

                # 6. Salva a aposta
                aposta = serializer.save(usuario=user_travado)

                # 7. Cria o extrato (Transação)
                Transacao.objects.create(
                    usuario=user_travado,
                    tipo='APOSTA',
                    valor=valor_aposta,
                    saldo_anterior=user_travado.saldo + valor_aposta,
                    saldo_posterior=user_travado.saldo,
                    descricao=f"Jogo: {aposta.get_tipo_jogo_display()} - {aposta.palpite}"
                )

                read_serializer = ApostaDetalheSerializer(aposta)
                return Response(read_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"erro": f"Erro interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)