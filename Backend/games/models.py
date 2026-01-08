from django.db import models
from django.conf import settings 
from django.core.cache import cache 
from .utils import (
    pegar_bicho, gerar_invertidas, extrair_resultado_completo, extrair_dezenas_sorteio,
    DEFAULT_COTACAO_QUININHA, DEFAULT_COTACAO_SENINHA, DEFAULT_COTACAO_LOTINHA
)

# --- ADICIONE ISTO AQUI (Funções para corrigir o Warning) ---
def get_default_quininha():
    return DEFAULT_COTACAO_QUININHA


def get_default_seninha():
    return DEFAULT_COTACAO_SENINHA


def get_default_lotinha():
    return DEFAULT_COTACAO_LOTINHA
# -----------------------------------------------------------

# 0. Configurações Globais (Singleton)
class ParametrosDoJogo(models.Model):
    # --- Cotações (Multiplicadores) ---
    # Baseado nos seus TIPOS_JOGO (G, D, C, M)
    cotacao_grupo = models.DecimalField("Grupo (18x)", max_digits=6, decimal_places=2, default=18.0)
    cotacao_dezena = models.DecimalField("Dezena (60x)", max_digits=6, decimal_places=2, default=60.0)
    cotacao_centena = models.DecimalField("Centena (600x)", max_digits=6, decimal_places=2, default=600.0)
    cotacao_milhar = models.DecimalField("Milhar (4000x)", max_digits=6, decimal_places=2, default=4000.0)
    
    # Cotações Combinadas
    cotacao_milhar_centena = models.DecimalField("Milhar/Centena (4400x)", max_digits=7, decimal_places=2, default=4400.0)
    cotacao_milhar_invertida = models.DecimalField("Milhar Invertida", max_digits=7, decimal_places=2, default=8000.0)
    cotacao_centena_invertida = models.DecimalField("Centena Invertida", max_digits=6, decimal_places=2, default=800.0)
    
    cotacao_duque_grupo = models.DecimalField("Duque de Grupo", max_digits=6, decimal_places=2, default=200.0)
    cotacao_terno_grupo = models.DecimalField("Terno de Grupo", max_digits=6, decimal_places=2, default=1500.0)
    cotacao_quadra_grupo = models.DecimalField("Quadra de Grupo", max_digits=6, decimal_places=2, default=1000.0)
    cotacao_quina_grupo = models.DecimalField("Quina de Grupo", max_digits=6, decimal_places=2, default=1000.0)
    
    cotacao_passe_vai = models.DecimalField("Passe Vai", max_digits=6, decimal_places=2, default=90.0)
    cotacao_passe_vai_vem = models.DecimalField("Passe Vai e Vem", max_digits=6, decimal_places=2, default=45.0)

    # 1. Acertos necessários (Editável no Admin)
    quininha_acertos_necessarios = models.IntegerField("Quininha - Acertos p/ Ganhar", default=5, help_text="Padrão: 5")
    seninha_acertos_necessarios = models.IntegerField("Seninha - Acertos p/ Ganhar", default=6, help_text="Padrão: 6")
    lotinha_acertos_necessarios = models.IntegerField("Lotinha - Acertos p/ Ganhar", default=5, help_text="Padrão: 5")

    # 2. Tabelas JSON (Quanto paga)
    tabela_quininha = models.JSONField("Tabela Pagamento Quininha", default=get_default_quininha)
    tabela_seninha = models.JSONField("Tabela Pagamento Seninha", default=get_default_seninha)
    tabela_lotinha = models.JSONField("Tabela Pagamento Lotinha", default=get_default_lotinha)

    # --- Segurança Financeira ---
    premio_maximo_aposta = models.DecimalField(
        "Teto Máximo (R$)", 
        max_digits=10, 
        decimal_places=2, 
        default=20000.00,
        help_text="Valor máximo que o sistema paga em uma única aposta."
    )
    ativa_apostas = models.BooleanField("Sistema Ativo?", default=True)

    class Meta:
        verbose_name = "Parâmetros do Jogo (Cotações)"
        verbose_name_plural = "Parâmetros do Jogo (Cotações)"

    def save(self, *args, **kwargs):
        self.pk = 1
        super(ParametrosDoJogo, self).save(*args, **kwargs)
        cache.set('parametros_jogo', self)

    def delete(self, *args, **kwargs):
        pass # Impede deletar

    @classmethod
    def load(cls):
        obj = cache.get('parametros_jogo')
        if obj is None:
            obj, created = cls.objects.get_or_create(pk=1)
            cache.set('parametros_jogo', obj)
        return obj

# 1. Tabela Auxiliar para os Bichos (Ex: 1=Avestruz, 25=Vaca)
class Bicho(models.Model):
    numero = models.IntegerField(primary_key=True) # 1 a 25
    nome = models.CharField(max_length=50)
    # Armazena as dezenas como texto (ex: "01,02,03,04") para facilitar
    dezenas = models.CharField(max_length=20) 

    def __str__(self):
        return f"{self.numero} - {self.nome}"

# 2. O Sorteio (A Extração)
class Sorteio(models.Model):
    HORARIOS_CHOICES = [
        ('PTM', 'PTM - 11:30'),
        ('PT', 'PT - 14:30'),
        ('PTV', 'PTV - 16:30'),
        ('FED', 'Federal - 19:00'),
        ('COR', 'Corujinha - 21:30'),
    ]

    data = models.DateField()
    horario = models.CharField(max_length=3, choices=HORARIOS_CHOICES)
    fechado = models.BooleanField(default=False) # Se True, não aceita mais apostas
    
    # Os 5 prêmios (Milhares sorteadas)
    premio_1 = models.CharField(max_length=4, blank=True, null=True)
    premio_2 = models.CharField(max_length=4, blank=True, null=True)
    premio_3 = models.CharField(max_length=4, blank=True, null=True)
    premio_4 = models.CharField(max_length=4, blank=True, null=True)
    premio_5 = models.CharField(max_length=4, blank=True, null=True)

    def __str__(self):
        return f"{self.get_horario_display()} - {self.data}"
    
    def apurar_resultados(self):
        """
        Processa todas as apostas vinculadas a este sorteio.
        """
        from django.db import transaction 
        
        # Se não tiver o 1º prêmio cadastrado, não faz nada
        if not self.premio_1:
            return False

        with transaction.atomic():
            # Itera sobre todas as apostas desse sorteio e trava as linhas no banco
            for aposta in self.apostas.select_for_update():
                
                # Verifica se ganhou
                ganhou = aposta.verificar_acerto()
                
                if ganhou:
                    aposta.ganhou = True
                    aposta.valor_premio = aposta.calcular_premio_estimado()
                else:
                    aposta.ganhou = False
                    aposta.valor_premio = 0.00
                
                aposta.save()

            # Fecha o sorteio automaticamente após processar
            self.fechado = True
            self.save()
            
        return True

# 3. A Aposta (O Ticket)
class Aposta(models.Model):
    TIPOS_JOGO = [
        # --- BÁSICOS ---
        ('G', 'Grupo'),           
        ('D', 'Dezena'),          
        ('C', 'Centena'),         
        ('M', 'Milhar'),          
        ('MC', 'Milhar/Centena'), 

        # --- NOVOS ---
        ('DG', 'Dupla de Grupo'),
        ('TG', 'Terno de Grupo'),
        ('QG', 'Quadra de Grupo'),
        ('QNG', 'Quina de Grupo'),
        ('DD', 'Duque de Dezena'),
        ('TD', 'Terno de Dezena'),
        ('PV', 'Passe Vai'),
        ('PVV', 'Passe Vai e Vem'),
        ('MI', 'Milhar Invertida'),
        ('CI', 'Centena Invertida'),
        ('DI', 'Dezena Invertida'),  
        ('MI', 'Milhar Invertida'),
        ('CI', 'Centena Invertida'),
        ('DI', 'Dezena Invertida'), 
    # --- Loterias ---
        ('QU', 'Quininha'), 
        ('SE', 'Seninha'), 
        ('LO', 'Lotinha'),
]                               

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='apostas')
    sorteio = models.ForeignKey(Sorteio, on_delete=models.PROTECT, related_name='apostas')
    
    tipo_jogo = models.CharField(max_length=3, choices=TIPOS_JOGO)
    valor = models.DecimalField(max_digits=10, decimal_places=2) # Quanto o usuário apostou
    
    # O palpite (Pode ser o número do grupo "16" ou a milhar "1234")
    palpite = models.CharField(max_length=255)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    ganhou = models.BooleanField(default=False)
    valor_premio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.usuario} - {self.get_tipo_jogo_display()} - {self.palpite}"
    

    def calcular_premio_estimado(self):
        config = ParametrosDoJogo.load() 
        multiplicador = 0.0

        # 1. CÁLCULO PARA LOTERIAS
        if self.tipo_jogo in ['QU', 'SE', 'LO']:
            qtde_jogada = str(len(self.palpite.replace('-', ',').split(',')))
            tabela = {}
            if self.tipo_jogo == 'QU': tabela = config.tabela_quininha
            elif self.tipo_jogo == 'SE': tabela = config.tabela_seninha
            elif self.tipo_jogo == 'LO': tabela = config.tabela_lotinha

            multiplicador = float(tabela.get(qtde_jogada, 0))

        # 2. CÁLCULO PARA JOGOS TRADICIONAIS
        elif self.tipo_jogo == 'G': multiplicador = config.cotacao_grupo
        elif self.tipo_jogo == 'D': multiplicador = config.cotacao_dezena
        elif self.tipo_jogo == 'C': multiplicador = config.cotacao_centena
        elif self.tipo_jogo == 'M': multiplicador = config.cotacao_milhar
        elif self.tipo_jogo == 'MC': multiplicador = config.cotacao_milhar_centena

        elif self.tipo_jogo == 'MI': multiplicador = config.cotacao_milhar_invertida
        elif self.tipo_jogo == 'CI': multiplicador = config.cotacao_centena_invertida

        elif self.tipo_jogo == 'DG': multiplicador = config.cotacao_duque_grupo
        elif self.tipo_jogo == 'TG': multiplicador = config.cotacao_terno_grupo
        elif self.tipo_jogo == 'QG': multiplicador = config.cotacao_quadra_grupo
        elif self.tipo_jogo == 'QNG': multiplicador = config.cotacao_quina_grupo

        elif self.tipo_jogo == 'PV': multiplicador = config.cotacao_passe_vai
        elif self.tipo_jogo == 'PVV': multiplicador = config.cotacao_passe_vai_vem

        premio = float(self.valor) * float(multiplicador)

        if premio > float(config.premio_maximo_aposta):
            premio = float(config.premio_maximo_aposta)

        return premio

    @staticmethod
    def descobrir_grupo(numero_str):
        """
        Converte número em bicho. Ex: '1234' -> Dezena 34 -> Grupo 9 (Cobra).
        """
        try:
            dezena = int(str(numero_str)[-2:])
            if dezena == 0: return 25
            return (dezena - 1) // 4 + 1
        except ValueError:
            return None

    def verificar_acerto(self):
        config = ParametrosDoJogo.load()

        if not self.sorteio or not self.sorteio.premio_1: return False 

        palpite_str = str(self.palpite).strip()

        # --- A. VALIDAÇÃO DE LOTERIAS ---
        if self.tipo_jogo in ['QU', 'SE', 'LO']:
            numeros_apostados = set([n.strip() for n in palpite_str.replace('-', ',').split(',')])
            dezenas_sorteadas = set(extrair_dezenas_sorteio(self.sorteio))

            qtd_acertos = len(numeros_apostados.intersection(dezenas_sorteadas))

            if self.tipo_jogo == 'QU': return qtd_acertos >= config.quininha_acertos_necessarios
            if self.tipo_jogo == 'SE': return qtd_acertos >= config.seninha_acertos_necessarios
            if self.tipo_jogo == 'LO': return qtd_acertos >= config.lotinha_acertos_necessarios
            return False

        # --- B. VALIDAÇÃO DO BICHO TRADICIONAL ---
        resultados = extrair_resultado_completo(self.sorteio)
        cabeca = resultados[0] if resultados else None
        if not cabeca: return False

        if self.tipo_jogo == 'M': return palpite_str == cabeca['milhar']
        elif self.tipo_jogo == 'C': return cabeca['milhar'].endswith(palpite_str)
        elif self.tipo_jogo == 'D': return cabeca['milhar'].endswith(palpite_str)
        elif self.tipo_jogo == 'G': return int(palpite_str) == cabeca['grupo']
        elif self.tipo_jogo == 'MC': return palpite_str == cabeca['milhar'] or cabeca['milhar'].endswith(palpite_str[1:])

        elif self.tipo_jogo == 'MI': return cabeca['milhar'] in gerar_invertidas(palpite_str)
        elif self.tipo_jogo == 'CI': return cabeca['centena'] in gerar_invertidas(palpite_str)

        elif self.tipo_jogo in ['DG', 'TG', 'QG', 'QNG']:
            grupos_apostados = [int(g) for g in palpite_str.replace('-',',').split(',')]
            grupos_sorteados = [r['grupo'] for r in resultados]
            acertos = set(grupos_apostados).intersection(set(grupos_sorteados))

            if self.tipo_jogo == 'DG': return len(acertos) >= 2
            if self.tipo_jogo == 'TG': return len(acertos) >= 3
            if self.tipo_jogo == 'QG': return len(acertos) >= 4
            if self.tipo_jogo == 'QNG': return len(acertos) >= 5

        elif self.tipo_jogo == 'PV':
            grupos_apostados = [int(g) for g in palpite_str.replace('-',',').split(',')]
            if len(grupos_apostados) < 2: return False
            if cabeca['grupo'] != grupos_apostados[0]: return False
            restante = [r['grupo'] for r in resultados[1:]]
            return grupos_apostados[1] in restante

        elif self.tipo_jogo == 'PVV':
             grupos_apostados = [int(g) for g in palpite_str.replace('-',',').split(',')]
             grupos_sorteados = [r['grupo'] for r in resultados]
             acertos = set(grupos_apostados).intersection(set(grupos_sorteados))
             return len(acertos) >= 2

        return False