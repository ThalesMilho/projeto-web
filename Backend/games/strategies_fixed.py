from abc import ABC, abstractmethod
from decimal import Decimal
from .utils import descobrir_bicho 

class RegraJogoStrategy(ABC):
    @abstractmethod
    def verificar(self, aposta, sorteio):
        pass

    def _get_premios_para_conferencia(self, sorteio, colocacao):
        todos_premios = [
            sorteio.premio_1, sorteio.premio_2, sorteio.premio_3,
            sorteio.premio_4, sorteio.premio_5
        ]
        
        nome_colocacao = colocacao.nome.upper() if colocacao else "CABEÇA"
        
        if "CABEÇA" in nome_colocacao or "1º" in nome_colocacao:
            return [todos_premios[0]]
        elif "1" in nome_colocacao and "5" in nome_colocacao:
            return todos_premios
        else:
            return [todos_premios[0]]

    def _formatar_numero_com_zeros(self, numero, digitos):
        """Helper para manter zeros à esquerda"""
        if not numero:
            return None
        str_num = str(numero).zfill(digitos)
        return str_num[-digitos:]

class RegraBichoExata(RegraJogoStrategy):
    def __init__(self, quantidade_digitos):
        self.q_digitos = quantidade_digitos

    def verificar(self, aposta, sorteio):
        premios_alvo = self._get_premios_para_conferencia(sorteio, aposta.colocacao)
        palpites_usuario = [str(p) for p in aposta.palpites]

        for premio in premios_alvo:
            if not premio: continue
            
            # CORRECTED: Mantém zeros à esquerda
            final_sorteado = self._formatar_numero_com_zeros(premio, self.q_digitos)
            if not final_sorteado:
                continue
            
            # CORRECTED: Formata palpites com zeros à esquerda também
            for palpite in palpites_usuario:
                palpite_formatado = self._formatar_numero_com_zeros(palpite, self.q_digitos)
                if palpite_formatado == final_sorteado:
                    return True
                
        return False

class RegraGrupo(RegraJogoStrategy):
    def verificar(self, aposta, sorteio):
        premios_alvo = self._get_premios_para_conferencia(sorteio, aposta.colocacao)
        palpites_usuario = [int(p) for p in aposta.palpites]

        for premio in premios_alvo:
            if not premio: continue
            
            grupo_sorteado = descobrir_bicho(premio)
            if grupo_sorteado is None:  # ADDED: Null check
                continue
            
            if grupo_sorteado in palpites_usuario:
                return True
                
        return False

class RegraCombinada(RegraJogoStrategy):
    def __init__(self, quantidade_acertos_necessarios):
        self.qtd_necessaria = quantidade_acertos_necessarios

    def verificar(self, aposta, sorteio):
        todos_premios = [
            sorteio.premio_1, sorteio.premio_2, sorteio.premio_3, 
            sorteio.premio_4, sorteio.premio_5
        ]
        
        grupos_sorteados = set()
        for premio in todos_premios:
            if premio:
                grupo = descobrir_bicho(premio)
                if grupo:  # ADDED: Skip null groups
                    grupos_sorteados.add(grupo)
        
        grupos_apostados = set([int(p) for p in aposta.palpites])
        acertos = grupos_apostados.intersection(grupos_sorteados)
        
        return len(acertos) >= self.qtd_necessaria

class RegraInvertida(RegraJogoStrategy):
    def __init__(self, quantidade_digitos):
        self.q_digitos = quantidade_digitos

    def verificar(self, aposta, sorteio):
        from itertools import permutations
        
        premios_alvo = self._get_premios_para_conferencia(sorteio, aposta.colocacao)
        palpite_base = str(aposta.palpites[0])
        
        # SECURITY: Limit permutations to prevent DoS
        if len(palpite_base) > 6:
            return False
            
        todas_combinacoes = set([''.join(p) for p in permutations(palpite_base)])
        
        for premio in premios_alvo:
            if not premio: continue
            final_sorteado = self._formatar_numero_com_zeros(premio, self.q_digitos)
            if not final_sorteado:
                continue
            
            if final_sorteado in todas_combinacoes:
                return True
                
        return False

# NEW: Lottery Variant Strategies
class RegraLotinha(RegraJogoStrategy):
    """Lottery-style intersection counting"""
    def __init__(self, acertos_necessarios=5):
        self.acertos_necessarios = acertos_necessarios

    def verificar(self, aposta, sorteio):
        from .utils import extrair_dezenas_sorteio
        
        # Get drawn numbers as sets for proper comparison
        dezenas_sorteadas = set(extrair_dezenas_sorteio(sorteio))
        palpites_usuario = set([str(p).zfill(2) for p in aposta.palpites])
        
        # Intersection count (order-independent)
        acertos = len(palpites_usuario.intersection(dezenas_sorteadas))
        return acertos >= self.acertos_necessarios

class ValidadorFactory:
    @staticmethod
    def get_strategy(modalidade):
        nome = modalidade.nome.upper()
        
        # Lottery variants (NEW)
        if "LOTINHA" in nome:
            return RegraLotinha()
        if "QUININHA" in nome:
            return RegraLotinha(acertos_necessarios=4)
        if "SENINHA" in nome:
            return RegraLotinha(acertos_necessarios=6)
        
        # Inversion games
        if "INVERTIDA" in nome:
            if "MILHAR" in nome: return RegraInvertida(4)
            if "CENTENA" in nome: return RegraInvertida(3)

        # Combined games
        if "DUQUE" in nome and "GRUPO" in nome:
            return RegraCombinada(2)
        if "TERNO" in nome and "GRUPO" in nome:
            return RegraCombinada(3)

        # Exact matches
        if "MILHAR" in nome: return RegraBichoExata(4)
        if "CENTENA" in nome: return RegraBichoExata(3)
        if "DEZENA" in nome: return RegraBichoExata(2)
        
        # Group
        if "GRUPO" in nome: return RegraGrupo()
        
        return None
