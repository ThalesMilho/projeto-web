from abc import ABC, abstractmethod
from decimal import Decimal
# Assumindo que você tem funções utilitárias para descobrir o bicho/grupo
from .utils import descobrir_bicho 

class RegraJogoStrategy(ABC):
    """
    Classe base. Define o contrato que toda regra de jogo deve seguir.
    """
    @abstractmethod
    def verificar(self, aposta, sorteio):
        """Retorna True/False ou a quantidade de acertos"""
        pass

    def _get_premios_para_conferencia(self, sorteio, colocacao):
        """
        Define quais linhas do sorteio vamos olhar baseados na Colocação.
        """
        # Lista com os valores dos prêmios: [premio_1, premio_2, ..., premio_5]
        todos_premios = [
            sorteio.premio_1, sorteio.premio_2, sorteio.premio_3,
            sorteio.premio_4, sorteio.premio_5
        ]
        
        # Lógica de negócio: Se a colocação for "Cabeça", olha só o índice 0.
        # Se for "1 ao 5", olha a lista inteira.
        nome_colocacao = colocacao.nome.upper() if colocacao else "CABEÇA"
        
        if "CABEÇA" in nome_colocacao or "1º" in nome_colocacao:
            return [todos_premios[0]] # Apenas o primeiro
        elif "1" in nome_colocacao and "5" in nome_colocacao: # Ex: "1 ao 5"
            return todos_premios
        else:
            # Fallback seguro: Cabeça
            return [todos_premios[0]]

# --- ESTRATÉGIAS CONCRETAS ---

class RegraBichoExata(RegraJogoStrategy):
    """
    Cobre: Milhar, Centena, Dezena.
    Lógica: O final do prêmio sorteado deve ser igual ao palpite.
    """
    def __init__(self, quantidade_digitos):
        self.q_digitos = quantidade_digitos

    def verificar(self, aposta, sorteio):
        premios_alvo = self._get_premios_para_conferencia(sorteio, aposta.colocacao)
        
        # Palpites do usuário (JSON List). Ex: ["1234"]
        # Se for aposta simples, pega o primeiro. Se permitir teimosinha/múltiplos, itera.
        palpites_usuario = [str(p) for p in aposta.palpites]

        for premio in premios_alvo:
            if not premio: continue
            
            # Extrai o final do prêmio (Ex: "1234" -> "234" se for centena)
            final_sorteado = premio[-self.q_digitos:]
            
            # Verifica se ALGUM palpite do usuário bate com ESSE prêmio
            if any(p[-self.q_digitos:] == final_sorteado for p in palpites_usuario):
                return True
                
        return False

class RegraGrupo(RegraJogoStrategy):
    """
    Cobre: Grupo (Seco ou 1 ao 5).
    Lógica: Converte o prêmio em Grupo e compara.
    """
    def verificar(self, aposta, sorteio):
        premios_alvo = self._get_premios_para_conferencia(sorteio, aposta.colocacao)
        palpites_usuario = [int(p) for p in aposta.palpites] # Ex: [15, 20]

        for premio in premios_alvo:
            if not premio: continue
            
            # Usa sua função utilitária existente para saber qual bicho deu
            grupo_sorteado = descobrir_bicho(premio) 
            
            if grupo_sorteado in palpites_usuario:
                return True
                
        return False

class RegraCombinada(RegraJogoStrategy):
    """
    Cobre: Duque de Grupo, Terno de Grupo.
    Lógica: Verifica se TODOS os grupos apostados apareceram nos 5 prêmios (ou na faixa).
    Diferença: Aqui precisamos acertar X grupos DENTRO dos prêmios sorteados.
    """
    def __init__(self, quantidade_acertos_necessarios):
        self.qtd_necessaria = quantidade_acertos_necessarios

    def verificar(self, aposta, sorteio):
        # Para Duque/Terno, geralmente olhamos SEMPRE do 1 ao 5 (Regra Padrão)
        # Mas podemos respeitar a colocação se o negócio exigir.
        todos_premios = [
            sorteio.premio_1, sorteio.premio_2, sorteio.premio_3, 
            sorteio.premio_4, sorteio.premio_5
        ]
        
        # Quais grupos deram no sorteio?
        grupos_sorteados = set()
        for premio in todos_premios:
            if premio:
                grupos_sorteados.add(descobrir_bicho(premio))
        
        # Quais grupos o usuário apostou?
        grupos_apostados = set([int(p) for p in aposta.palpites])
        
        # Interseção: Quais grupos ele acertou?
        acertos = grupos_apostados.intersection(grupos_sorteados)
        
        # Se acertou a quantidade necessária (Ex: 2 para Duque, 3 para Terno)
        return len(acertos) >= self.qtd_necessaria

class RegraInvertida(RegraJogoStrategy):
    """
    Cobre: Milhar/Centena Invertida.
    Lógica: Gera todas as permutações do palpite e verifica se alguma bateu.
    (Implementação avançada que faltava)
    """
    from itertools import permutations

    def __init__(self, quantidade_digitos):
        self.q_digitos = quantidade_digitos

    def verificar(self, aposta, sorteio):
        from itertools import permutations
        
        premios_alvo = self._get_premios_para_conferencia(sorteio, aposta.colocacao)
        palpite_base = str(aposta.palpites[0]) # Ex: "1234"
        
        # Gera todas as permutações possíveis. Ex: 1234, 4321, 1324...
        todas_combinacoes = set([''.join(p) for p in permutations(palpite_base)])
        
        for premio in premios_alvo:
            if not premio: continue
            final_sorteado = premio[-self.q_digitos:]
            
            if final_sorteado in todas_combinacoes:
                return True
                
        return False

# --- FACTORY ATUALIZADA ---

class ValidadorFactory:
    @staticmethod
    def get_strategy(modalidade):
        nome = modalidade.nome.upper()
        
        # 1. Jogos de Inversão
        if "INVERTIDA" in nome:
            if "MILHAR" in nome: return RegraInvertida(4)
            if "CENTENA" in nome: return RegraInvertida(3)

        # 2. Jogos Combinados (Duque/Terno)
        if "DUQUE" in nome and "GRUPO" in nome:
            return RegraCombinada(2)
        if "TERNO" in nome and "GRUPO" in nome:
            return RegraCombinada(3)

        # 3. Jogos Exatos (Milhar, Centena, Dezena)
        if "MILHAR" in nome: return RegraBichoExata(4)
        if "CENTENA" in nome: return RegraBichoExata(3)
        if "DEZENA" in nome: return RegraBichoExata(2)
        
        # 4. Grupo Simples
        if "GRUPO" in nome: return RegraGrupo()
        
        return None