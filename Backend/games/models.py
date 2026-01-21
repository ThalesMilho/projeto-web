from decimal import Decimal, ROUND_DOWN 
from django.db import models
from django.conf import settings 
from django.core.cache import cache 

from .utils import (
    pegar_bicho, gerar_invertidas, extrair_resultado_completo, extrair_dezenas_sorteio,
    DEFAULT_COTACAO_QUININHA, DEFAULT_COTACAO_SENINHA, DEFAULT_COTACAO_LOTINHA
)

def get_default_quininha():
    return DEFAULT_COTACAO_QUININHA


def get_default_seninha():
    return DEFAULT_COTACAO_SENINHA


def get_default_lotinha():
    return DEFAULT_COTACAO_LOTINHA
# -----------------------------------------------------------

# Em Backend/games/models.py

# ... imports ...

class SingletonModel(models.Model):
    """
    Classe abstrata para garantir que só exista 1 registro desta tabela (Configurações).
    """
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class ParametrosDoJogo(SingletonModel):
    # --- Cotações do Jogo do Bicho ---
    cotacao_grupo = models.DecimalField("Grupo (18x)", max_digits=6, decimal_places=2, default=18.0)
    cotacao_dezena = models.DecimalField("Dezena (60x)", max_digits=6, decimal_places=2, default=60.0)
    cotacao_centena = models.DecimalField("Centena (600x)", max_digits=6, decimal_places=2, default=600.0)
    cotacao_milhar = models.DecimalField("Milhar (4000x)", max_digits=6, decimal_places=2, default=4000.0)
    
    # Invertidas e Combinadas
    cotacao_milhar_invertida = models.DecimalField("Milhar Invertida", max_digits=6, decimal_places=2, default=400.0)
    cotacao_centena_invertida = models.DecimalField("Centena Invertida", max_digits=6, decimal_places=2, default=100.0)
    cotacao_duque_dezena = models.DecimalField("Duque de Dezena", max_digits=6, decimal_places=2, default=300.0)
    cotacao_terno_dezena = models.DecimalField("Terno de Dezena", max_digits=6, decimal_places=2, default=3000.0)
    cotacao_passe_vai_vem = models.DecimalField("Passe Vai-Vem", max_digits=6, decimal_places=2, default=40.0)
    cotacao_milhar_centena = models.DecimalField("Milhar/Centena", max_digits=6, decimal_places=2, default=2000.0)

    cotacao_duque_grupo = models.DecimalField("Duque de Grupo", max_digits=6, decimal_places=2, default=18.0)
    cotacao_terno_grupo = models.DecimalField("Terno de Grupo", max_digits=6, decimal_places=2, default=150.0)
    cotacao_quadra_grupo = models.DecimalField("Quadra de Grupo", max_digits=6, decimal_places=2, default=1000.0)
    cotacao_quina_grupo = models.DecimalField("Quina de Grupo", max_digits=6, decimal_places=2, default=5000.0)
    cotacao_passe_vai = models.DecimalField("Passe Vai", max_digits=6, decimal_places=2, default=80.0)

    cotacao_quininha = models.JSONField(
        default=get_default_quininha, 
        verbose_name="Tabela Quininha (Ex: {'1': 10, '5': 1000})"
    )
    cotacao_seninha = models.JSONField(
        default=get_default_seninha,
        verbose_name="Tabela Seninha"
    )
    cotacao_lotinha = models.JSONField(
        default=get_default_lotinha,
        verbose_name="Tabela Lotinha"
    )

    quininha_acertos_necessarios = models.IntegerField("Quininha (Acertos Min)", default=1)
    seninha_acertos_necessarios = models.IntegerField("Seninha (Acertos Min)", default=1)
    lotinha_acertos_necessarios = models.IntegerField("Lotinha (Acertos Min)", default=1)

    modalidades_ativas = models.JSONField(
        default=dict, 
        blank=True,
        verbose_name="Modalidades Ativas (JSON)",
        help_text="Ex: {'M': true, 'G': false}"
    )

    milhar_brinde_ativa = models.BooleanField("Promoção Milhar Brinde Ativa?", default=False)
    valor_minimo_para_brinde = models.DecimalField(
        "Mínimo para ganhar Brinde (R$)", 
        max_digits=10, decimal_places=2, default=Decimal('20.00')
    )
    cotacao_milhar_brinde = models.DecimalField(
        "Cotação da Milhar Brinde", 
        max_digits=10, decimal_places=2, default=Decimal('1000.00')
    )

    # --- Kill Switch & Regras Gerais ---
    ativa_apostas = models.BooleanField("Sistema Ativo?", default=True)
    
    limite_saque_automatico = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('500.00'),
        verbose_name="Teto para Saque Automático (R$)"
    )
    tempo_minimo_deposito_saque_minutos = models.IntegerField(
        default=120, # 2 horas
        verbose_name="Tempo Mínimo entre Depósito e Saque (min)"
    )

    premio_maximo_aposta = models.DecimalField(
        "Prêmio Máximo por Aposta (R$)", 
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('20000.00')
    )

    def __str__(self):
        return "Configurações do Sistema"

    class Meta:
        verbose_name = "Parâmetros do Sistema"
        verbose_name_plural = "Parâmetros do Sistema"

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
    valor_premio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Comissão gerada para cambistas
    comissao_gerada = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.usuario} - {self.get_tipo_jogo_display()} - {self.palpite}"
    

    def calcular_premio_estimado(self):
        config = ParametrosDoJogo.load() 
        
        # Garante que o valor é Decimal
        valor_aposta = Decimal(str(self.valor))
        multiplicador = Decimal('0.00')

        # 1. CÁLCULO PARA LOTERIAS (Baseado em JSON)
        if self.tipo_jogo in ['QU', 'SE', 'LO']:
            # Limpeza robusta da string (Remove espaços e vazios)
            numeros = [n.strip() for n in self.palpite.replace('-', ',').split(',') if n.strip()]
            qtde_jogada = str(len(numeros))
            
            tabela = {}
            if self.tipo_jogo == 'QU': tabela = config.cotacao_quininha
            elif self.tipo_jogo == 'SE': tabela = config.cotacao_seninha
            elif self.tipo_jogo == 'LO': tabela = config.cotacao_lotinha

            # Pega o valor da tabela (padrão 0 se não achar) e converte pra Decimal
            fator = tabela.get(qtde_jogada, 0)
            multiplicador = Decimal(str(fator))

        # 2. CÁLCULO PARA JOGOS TRADICIONAIS
        # Mapeamento direto para evitar IFs gigantes
        mapa_cotacoes = {
            'G': config.cotacao_grupo,
            'D': config.cotacao_dezena,
            'C': config.cotacao_centena,
            'M': config.cotacao_milhar,
            'MC': config.cotacao_milhar_centena if hasattr(config, 'cotacao_milhar_centena') else Decimal('0'),
            'MI': config.cotacao_milhar_invertida,
            'CI': config.cotacao_centena_invertida,
            'DG': config.cotacao_duque_grupo if hasattr(config, 'cotacao_duque_grupo') else Decimal('0'),
            'PV': config.cotacao_passe_vai,
            'PVV': config.cotacao_passe_vai_vem,
        }

        if self.tipo_jogo in mapa_cotacoes:
            multiplicador = mapa_cotacoes[self.tipo_jogo]

        # Cálculo Final Seguro
        premio = valor_aposta * multiplicador

        # Verifica limite máximo (se tiver esse campo no config, senão ignore)
        if hasattr(config, 'premio_maximo_aposta') and premio > config.premio_maximo_aposta:
            premio = config.premio_maximo_aposta

        # Arredonda para 2 casas decimais para baixo (padrão bancário para evitar pagar a mais)
        return premio.quantize(Decimal('0.01'), rounding=ROUND_DOWN)

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