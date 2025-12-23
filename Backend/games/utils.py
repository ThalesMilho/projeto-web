import math

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