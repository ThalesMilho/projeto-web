import math
from itertools import permutations

# --- 1. CONFIGURAÇÃO INICIAL (DEFAULTS) ---
# Estes valores vão para o Banco de Dados na criação dos parâmetros.

# Quininha: Paga X vezes dependendo de quantas dezenas o usuário jogou
DEFAULT_COTACAO_QUININHA = {
    "13": 5000.0, "14": 3900.0, "15": 2700.0, "16": 2200.0, 
    "17": 1600.0, "18": 1100.0, "19": 800.0,  "20": 700.0, 
    "25": 180.0,  "30": 65.0,   "35": 29.0,   "40": 10.0,   "45": 7.0
}

# Seninha: Exemplo de cotação para acerto de 6 dezenas
DEFAULT_COTACAO_SENINHA = {
    "14": 5000.0, "15": 3500.0, "16": 2000.0, "17": 1500.0,
    "18": 850.0,  "19": 650.0,  "20": 500.0,  "25": 110.0,
    "30": 28.0,   "35": 8.0,    "40": 5.0
}

# Lotinha: Exemplo de cotação para acerto (geralmente 5 dezenas com cotação diferente)
DEFAULT_COTACAO_LOTINHA = {
    "16": 5000.0, "17": 200.0, "18": 100.0, "19": 50.0,
    "20": 25.0,   "21": 15.0,  "22": 8.0
}

# --- 2. FUNÇÕES AUXILIARES DE CÁLCULO ---

def pegar_bicho(numero_str):
    """
    Retorna o número do grupo (1-25) baseado na string numérica.
    Ex: '1234' -> 09 (Cobra)
    """
    try:
        if not numero_str: return None
        dezena = int(str(numero_str)[-2:])
        if dezena == 0: return 25
        return math.ceil(dezena / 4)
    except:
        return None

def gerar_invertidas(palpite_str):
    """
    Gera todas as permutações únicas para apostas invertidas.
    Ex: '123' -> ['123', '132', '213', '231', '312', '321']
    """
    perms = set([''.join(p) for p in permutations(palpite_str)])
    return list(perms)

def extrair_dezenas_sorteio(sorteio):
    """
    Retorna uma LISTA com todas as dezenas sorteadas (do 1º ao 10º prêmio).
    Usado para conferir Quininha, Seninha, etc.
    """
    dezenas = []
    # Verifica dinamicamente até o 10º prêmio
    campos_premios = [
        'premio_1', 'premio_2', 'premio_3', 'premio_4', 'premio_5',
        'premio_6', 'premio_7', 'premio_8', 'premio_9', 'premio_10'
    ]
    
    for campo in campos_premios:
        # getattr garante que não quebre se o campo ainda não existir na migração antiga
        valor = getattr(sorteio, campo, None) 
        if valor and len(str(valor)) >= 2:
            dezenas.append(str(valor)[-2:]) # Pega os últimos 2 dígitos (Dezena)
            
    return dezenas

def extrair_resultado_completo(sorteio):
    """
    Retorna estrutura detalhada dos 5 primeiros prêmios para validação de Bicho.
    """
    resultados = []
    premios_raw = [
        sorteio.premio_1, sorteio.premio_2, sorteio.premio_3, 
        sorteio.premio_4, sorteio.premio_5
    ]
    
    for i, numero in enumerate(premios_raw):
        if numero:
            resultados.append({
                'posicao': i + 1,
                'milhar': numero,
                'centena': numero[-3:],
                'dezena': numero[-2:],
                'grupo': pegar_bicho(numero)
            })
    return resultados

def descobrir_bicho(milhar_string):
    """
    Recebe uma string (ex: '1234' ou '55') e retorna o número do bicho (1-25).
    """
    try:
        # Pega apenas os últimos 2 dígitos (a dezena)
        dezena = int(milhar_string[-2:])
        
        if dezena == 0:
            return 25 # 00 é Vaca
        
        # A matemática mágica do Jogo do Bicho
        # Ex: Dezena 01 a 04 / 4 = 0.something -> teto é 1 (Avestruz)
        bicho = math.ceil(dezena / 4)
        return bicho
    except:
        return None
    
