from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.db import transaction 
from django.db.models import F 
from .models import Sorteio
from .serializer import SorteioSerializer, CriarApostaSerializer
from django.shortcuts import get_object_or_404
from .utils import descobrir_bicho 
from decimal import Decimal
from .models import Sorteio, Aposta
from django.shortcuts import render 
from accounts.models import Transacao
import math
from collections import Counter

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
            # --- PRINCIPAIS ---
            {"modalidade": "M", "nome": "Milhar", "fator": 6000.0, "destaque": True}, 
            {"modalidade": "C", "nome": "Centena", "fator": 600.0},
            {"modalidade": "D", "nome": "Dezena", "fator": 60.0},
            {"modalidade": "G", "nome": "Grupo", "fator": 18.0},
            {"modalidade": "MC", "nome": "Milhar/Centena", "fator": 3300.0},

            # --- ESPECIAIS ---
            {"modalidade": "DG", "nome": "Dupla de Grupo", "fator": 16.0},
            {"modalidade": "TG", "nome": "Terno de Grupo", "fator": 150.0},
            {"modalidade": "QG", "nome": "Quadra de Grupo", "fator": 1000.0},
            {"modalidade": "QNG", "nome": "Quina de Grupo", "fator": 5000.0},
            {"modalidade": "DD", "nome": "Duque de Dezena", "fator": 300.0},
            {"modalidade": "TD", "nome": "Terno de Dezena", "fator": 5000.0},
            {"modalidade": "PV", "nome": "Passe Vai", "fator": 90.0},
            {"modalidade": "PVV", "nome": "Passe Vai e Vem", "fator": 90.0},
            {"modalidade": "MI", "nome": "Milhar Invertida", "fator": 6000.0},
            {"modalidade": "CI", "nome": "Centena Invertida", "fator": 600.0},
            {"modalidade": "DI", "nome": "Dezena Invertida", "fator": 60.0},
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
    Tudo isso dentro de uma transação atômica.
    """
    permission_classes = [IsAuthenticated] # Só logado aposta!

    def post(self, request):
        serializer = CriarApostaSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            try:
                # Dados da aposta
                dados = serializer.validated_data
                user = request.user
                
                # --- ANTI-DUPLICAÇÃO (Dedup) ---
                # Verifica se o usuário fez exatamente a mesma aposta nos últimos 5 segundos
                tempo_limite = timezone.now() - timezone.timedelta(seconds=5)
                duplicada = Aposta.objects.filter(
                    usuario=user,
                    sorteio=dados['sorteio'],
                    tipo_jogo=dados['tipo_jogo'],
                    valor=dados['valor'],
                    palpite=dados['palpite'],
                    criado_em__gte=tempo_limite
                ).exists()

                if duplicada:
                    return Response(
                        {"erro": "Você já fez essa aposta agora mesmo. Verifique seu histórico."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

                with transaction.atomic():
                    # LOCK PESSIMISTA no usuário
                    user = type(request.user).objects.select_for_update().get(pk=user.pk)
                    
                    # Validação de Saldo
                    if user.saldo < dados['valor']:
                        return Response({"saldo": ["Saldo insuficiente."]}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # VALIDAÇÃO FINAL DE SORTEIO FECHADO
                    if dados['sorteio'].fechado:
                         return Response({"sorteio": ["Sorteio encerrado durante o processamento."]}, status=status.HTTP_400_BAD_REQUEST)

                    # Debita e Salva
                    user.saldo = F('saldo') - dados['valor']
                    user.total_apostado_rollover = F('total_apostado_rollover') + dados['valor'] 
                    
                    user.save(update_fields=['saldo', 'total_apostado_rollover']) 
                    user.refresh_from_db()

                    aposta_criada = serializer.save(usuario=user) 
                    
                    Transacao.objects.create(
                        usuario=user,
                        tipo='APOSTA',
                        valor=dados['valor'],
                        saldo_anterior=user.saldo + dados['valor'], 
                        saldo_posterior=user.saldo,
                        descricao=f"Aposta #{aposta_criada.id} - {aposta_criada.get_tipo_jogo_display()} - {aposta_criada.palpite}"
                    )
                    
                return Response(
                    {"mensagem": "Aposta realizada com sucesso!", "novo_saldo": user.saldo}, 
                    status=status.HTTP_201_CREATED
                )
            
            except Exception as e:
                # O "str(e)" vai nos contar se é NameError, DatabaseError, etc.
                return Response(
                    {"erro": f"ERRO DETALHADO: {str(e)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApuracaoView(APIView):
    """
    Motor de Apuração Avançado v2.0
    Suporta: Cabeça, Invertidas (com cálculo de cota), Passes, Duplas, Ternos, Quadras e Quinas.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # 1. Validações Iniciais
        if Sorteio.objects.filter(pk=pk, fechado=True).exists():
             return Response({"erro": "Este sorteio já foi apurado e fechado."}, status=status.HTTP_400_BAD_REQUEST)

        sorteio = get_object_or_404(Sorteio, pk=pk)
        
        # Garante que todos os 5 prêmios foram lançados
        premios_raw = [
            sorteio.premio_1, sorteio.premio_2, sorteio.premio_3, 
            sorteio.premio_4, sorteio.premio_5
        ]
        if not all(premios_raw):
            return Response({"erro": "Lance todos os 5 prêmios no Admin antes de apurar jogos complexos!"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Pré-Cálculo do Gabarito (Matriz de Resultados)
        # Cria uma lista de dicionários com todos os dados de cada prêmio (1 ao 5)
        gabarito = []
        for p in premios_raw:
            gabarito.append({
                'milhar': p,                  # "1234"
                'centena': p[-3:],            # "234"
                'dezena': p[-2:],             # "34"
                'bicho': descobrir_bicho(p)   # 9 (Cobra)
            })

        # Conjuntos para busca rápida (Set lookup é O(1))
        todos_bichos = {g['bicho'] for g in gabarito}       # Ex: {9, 25, 1, ...}
        todas_dezenas = {g['dezena'] for g in gabarito}     # Ex: {'34', '00', ...}
        
        # Cabeça (Prêmio 1) para modalidades clássicas
        cabeca = gabarito[0]

        vencedores_count = 0
        pagamentos_total = Decimal('0.00')

        try:
            with transaction.atomic():
                sorteio_travado = Sorteio.objects.select_for_update().get(pk=pk)
                if sorteio_travado.fechado:
                    return Response({"erro": "Concorrência: Sorteio fechado durante processamento."}, status=status.HTTP_400_BAD_REQUEST)

                apostas = Aposta.objects.filter(sorteio=sorteio_travado, ganhou=False).select_for_update()

                for aposta in apostas:
                    ganhou_aposta = False
                    multiplicador = Decimal('0.0')
                    tipo = aposta.tipo_jogo
                    palpite = aposta.palpite.strip()

                    # --- MODALIDADES DE CABEÇA (CLÁSSICAS) ---
                    if tipo == 'M' and palpite == cabeca['milhar']:
                        ganhou_aposta = True
                        multiplicador = Decimal('6000.0')

                    elif tipo == 'C' and palpite == cabeca['centena']:
                        ganhou_aposta = True
                        multiplicador = Decimal('600.0')

                    elif tipo == 'D' and palpite == cabeca['dezena']:
                        ganhou_aposta = True
                        multiplicador = Decimal('60.0')
                    
                    elif tipo == 'G' and int(palpite) == cabeca['bicho']:
                        ganhou_aposta = True
                        multiplicador = Decimal('18.0')

                    elif tipo == 'MC':
                        if palpite == cabeca['milhar']:
                            ganhou_aposta = True
                            multiplicador = Decimal('3300.0')
                        elif palpite[-3:] == cabeca['centena']:
                            ganhou_aposta = True
                            multiplicador = Decimal('300.0')

                    # --- MODALIDADES INVERTIDAS (Permutações na Cabeça) ---
                    elif tipo in ['MI', 'CI', 'DI']:
                        # Define alvo e base
                        if tipo == 'MI': 
                            alvo, base_fator = cabeca['milhar'], Decimal('6000.0')
                        elif tipo == 'CI': 
                            alvo, base_fator = cabeca['centena'], Decimal('600.0')
                        else:              
                            alvo, base_fator = cabeca['dezena'], Decimal('60.0')

                        # Lógica: Ordena as strings para ver se contêm os mesmos dígitos
                        # Ex: Palpite "1234" ganha de Resultado "4321" -> sorted("1234") == sorted("4321")
                        if sorted(palpite) == sorted(alvo):
                            ganhou_aposta = True
                            # Cálculo Matemático: Divide o prêmio pelo número de permutações possíveis
                            # Ex: "1234" tem 24 combinações. Prêmio é 6000/24 = 250x.
                            # Ex: "1122" tem 6 combinações. Prêmio é 6000/6 = 1000x.
                            counts = Counter(palpite)
                            permutacoes = math.factorial(len(palpite))
                            for count in counts.values():
                                permutacoes //= math.factorial(count)
                            
                            multiplicador = base_fator / Decimal(permutacoes)

                    # --- MODALIDADES DE GRUPO (1º ao 5º) ---
                    elif tipo in ['DG', 'TG', 'QG', 'QNG']:
                        # Helper: Transforma "01, 02" em [1, 2]
                        try:
                            grupos_apostados = {int(x) for x in palpite.replace(',', ' ').split() if x.strip()}
                        except ValueError:
                            continue # Pula aposta se palpite for inválido

                        # Verifica se TODOS os grupos apostados estão no sorteio (Subset)
                        if grupos_apostados.issubset(todos_bichos):
                            ganhou_aposta = True
                            if tipo == 'DG' and len(grupos_apostados) >= 2: multiplicador = Decimal('16.0')
                            elif tipo == 'TG' and len(grupos_apostados) >= 3: multiplicador = Decimal('150.0')
                            elif tipo == 'QG' and len(grupos_apostados) >= 4: multiplicador = Decimal('1000.0')
                            elif tipo == 'QNG' and len(grupos_apostados) >= 5: multiplicador = Decimal('5000.0')

                    # --- MODALIDADES DE DEZENA (1º ao 5º) ---
                    elif tipo in ['DD', 'TD']:
                        try:
                            dezenas_apostadas = {x.strip() for x in palpite.replace(',', ' ').split() if x.strip()}
                        except: continue

                        if dezenas_apostadas.issubset(todas_dezenas):
                            ganhou_aposta = True
                            if tipo == 'DD' and len(dezenas_apostadas) >= 2: multiplicador = Decimal('300.0')
                            elif tipo == 'TD' and len(dezenas_apostadas) >= 3: multiplicador = Decimal('5000.0')

                    # --- PASSES (Vai e Vai-Vem) ---
                    elif tipo in ['PV', 'PVV']:
                        try:
                            # Palpite esperado: "Grupo1, Grupo2"
                            parts = [int(x) for x in palpite.replace(',', ' ').split() if x.strip()]
                            if len(parts) >= 2:
                                g1, g2 = parts[0], parts[1]
                                
                                # PV: G1 na Cabeça + G2 em qualquer outro prêmio (2-5)
                                # PVV: (G1 na Cabeça + G2 no resto) OU (G2 na Cabeça + G1 no resto)
                                
                                # Lista de bichos do 2º ao 5º prêmio
                                bichos_resto = {g['bicho'] for g in gabarito[1:]} # Índices 1 a 4
                                
                                condicao_ida = (g1 == cabeca['bicho'] and g2 in bichos_resto)
                                condicao_volta = (g2 == cabeca['bicho'] and g1 in bichos_resto)

                                if tipo == 'PV' and condicao_ida:
                                    ganhou_aposta = True
                                    multiplicador = Decimal('90.0')
                                elif tipo == 'PVV' and (condicao_ida or condicao_volta):
                                    ganhou_aposta = True
                                    multiplicador = Decimal('90.0')
                        except:
                            continue

                    # --- PAGAMENTO ---
                    if ganhou_aposta:
                        premio = aposta.valor * multiplicador
                        aposta.ganhou = True
                        aposta.valor_premio = premio
                        aposta.save()
                        
                        # Atualiza Saldo do Usuário
                        user_update = type(aposta.usuario).objects.select_for_update().get(pk=aposta.usuario.pk)
                        saldo_ant = user_update.saldo
                        user_update.saldo = F('saldo') + premio
                        user_update.save()
                        user_update.refresh_from_db()
                        
                        # Gera Extrato
                        Transacao.objects.create(
                            usuario=user_update,
                            tipo='PREMIO',
                            valor=premio,
                            saldo_anterior=saldo_ant,
                            saldo_posterior=user_update.saldo,
                            descricao=f"Prêmio {aposta.get_tipo_jogo_display()} (Sorteio #{sorteio.id})"
                        )
                        vencedores_count += 1
                        pagamentos_total += premio
            
                sorteio_travado.fechado = True
                sorteio_travado.save()

            return Response({
                "mensagem": "Apuração Avançada concluída!",
                "vencedores": vencedores_count,
                "total_pago": pagamentos_total,
                "gabarito_bichos": list(todos_bichos) # Retorna quem deu pra conferência
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"erro": f"Erro Crítico na Apuração: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- VIEW VISUAL (HTML) ---

def comprovante_view(request, pk):
    """
    Renderiza o comprovante da aposta em HTML para impressão.
    """
    aposta = get_object_or_404(Aposta, pk=pk)
    return render(request, 'games/ticket.html', {'aposta': aposta})