from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.db import transaction # Importante para garantir que o dinheiro só sai se a aposta gravar
from .models import Sorteio
from .serializer import SorteioSerializer, CriarApostaSerializer
from django.shortcuts import get_object_or_404
from .utils import descobrir_bicho 
from decimal import Decimal
from .models import Sorteio, Aposta
from django.shortcuts import render 

# --- VIEWS DE LEITURA (GET - Públicas) ---

class BichosView(APIView):
    permission_classes = [AllowAny] 

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
    permission_classes = [AllowAny]

    def get(self, request):
        cotacoes = [
            {"modalidade": "G", "nome": "Grupo", "fator": 18.0},
            {"modalidade": "D", "nome": "Dezena", "fator": 60.0},
            {"modalidade": "C", "nome": "Centena", "fator": 600.0},
            {"modalidade": "M", "nome": "Milhar", "fator": 5000.0},
            {"modalidade": "MC", "nome": "Milhar/Centena", "fator": 2500.0}, 
        ]
        return Response(cotacoes, status=status.HTTP_200_OK)

class SorteiosAbertosView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        hoje = timezone.localdate()
        sorteios = Sorteio.objects.filter(
            data__gte=hoje, 
            fechado=False
        ).order_by('data', 'id') 

        serializer = SorteioSerializer(sorteios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)    

class QuininhaView(APIView):
    permission_classes = [AllowAny]
    
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
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

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

# --- VIEWS DE AÇÃO (POST - Protegidas) ---

class RealizarApostaView(APIView):
    """
    Recebe o pedido de aposta, valida saldo e sorteio, desconta o dinheiro e cria o bilhete.
    Tudo isso dentro de uma transação atômica (ou faz tudo, ou não faz nada).
    """
    permission_classes = [IsAuthenticated] # Só logado aposta!

    def post(self, request):
        # Passamos o context para o serializer ter acesso ao 'request.user'
        serializer = CriarApostaSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            try:
                # Inicia transação no banco (Segurança Financeira)
                with transaction.atomic():
                    user = request.user
                    valor = serializer.validated_data['valor']
                    
                    # 1. Debita o saldo
                    user.saldo -= valor
                    user.save()
                    
                    # 2. Cria a aposta vinculada ao usuário
                    serializer.save(usuario=user) 
                    
                return Response(
                    {"mensagem": "Aposta realizada com sucesso!", "novo_saldo": user.saldo}, 
                    status=status.HTTP_201_CREATED
                )
            
            except Exception as e:
                # Se der erro no banco, o saldo não é descontado (rollback automático)
                return Response(
                    {"erro": "Erro interno ao processar aposta. Tente novamente."}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ApuracaoView(APIView):
    """
    Rota Administrativa: Processa os vencedores de um sorteio.
    Suporta: GRUPO (18x), CENTENA (600x) e MILHAR (5000x).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        sorteio = get_object_or_404(Sorteio, pk=pk)
        
        # O Sorteio precisa ter o resultado lançado no Admin (Premio 1)
        if not sorteio.premio_1:
            return Response({"erro": "Lance o resultado (Prêmio 1) no Admin antes de apurar!"}, status=status.HTTP_400_BAD_REQUEST)

        # --- GABARITO DO SORTEIO ---
        resultado_milhar = sorteio.premio_1          # Ex: "1234"
        resultado_centena = resultado_milhar[-3:]    # Ex: "234"
        bicho_vencedor = descobrir_bicho(resultado_milhar) # Ex: 9 (Cobra)
        
        # Busca apostas pendentes deste sorteio
        apostas = Aposta.objects.filter(sorteio=sorteio, ganhou=False)
        
        vencedores_count = 0
        pagamentos_total = 0.0

        with transaction.atomic():
            for aposta in apostas:
                ganhou_aposta = False
                multiplicador = 0.0

                # --- REGRA 1: MILHAR (M) - Paga 5.000x ---
                if aposta.tipo_jogo == 'M':
                    if aposta.palpite == resultado_milhar: # Tem que ser igualzinho
                        ganhou_aposta = True
                        multiplicador = 5000.0

                # --- REGRA 2: CENTENA (C) - Paga 600x ---
                elif aposta.tipo_jogo == 'C':
                    if aposta.palpite == resultado_centena: # Últimos 3 dígitos
                        ganhou_aposta = True
                        multiplicador = 600.0

                # --- REGRA 3: GRUPO (G) - Paga 18x ---
                elif aposta.tipo_jogo == 'G':
                    # O palpite vem como string "1", convertemos pra int pra comparar com o bicho
                    if int(aposta.palpite) == bicho_vencedor:
                        ganhou_aposta = True
                        multiplicador = 18.0

                # --- PAGAMENTO ---
                if ganhou_aposta:
                    premio = float(aposta.valor) * multiplicador
                    
                    # 1. Marca como ganho
                    aposta.ganhou = True
                    aposta.valor_premio = premio
                    aposta.save()
                    
                    # 2. Paga o Usuário
                    usuario = aposta.usuario
                    usuario.saldo += Decimal(premio)
                    usuario.save()
                    
                    vencedores_count += 1
                    pagamentos_total += premio
        
        # Fecha o sorteio
        sorteio.fechado = True
        sorteio.save()

        return Response({
            "mensagem": "Apuração realizada com sucesso!",
            "resultados": {
                "milhar": resultado_milhar,
                "centena": resultado_centena,
                "bicho_vencedor": bicho_vencedor
            },
            "vencedores": vencedores_count,
            "total_pago": pagamentos_total
        }, status=status.HTTP_200_OK)
    

    # --- VIEW VISUAL (HTML) ---

def comprovante_view(request, pk):
    """
    Renderiza o comprovante da aposta em HTML para impressão.
    """
    aposta = get_object_or_404(Aposta, pk=pk)
    return render(request, 'games/ticket.html', {'aposta': aposta})