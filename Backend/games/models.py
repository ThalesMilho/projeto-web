from django.db import models
from django.conf import settings 
from django.core.cache import cache 

# 0. Configurações Globais (Singleton)
class ParametrosDoJogo(models.Model):
    # --- Cotações (Multiplicadores) ---
    # Baseado nos seus TIPOS_JOGO (G, D, C, M)
    cotacao_grupo = models.DecimalField("Grupo (18x)", max_digits=6, decimal_places=2, default=18.0)
    cotacao_dezena = models.DecimalField("Dezena (60x)", max_digits=6, decimal_places=2, default=60.0)
    cotacao_centena = models.DecimalField("Centena (600x)", max_digits=6, decimal_places=2, default=600.0)
    cotacao_milhar = models.DecimalField("Milhar (4000x)", max_digits=6, decimal_places=2, default=4000.0)
    
    # Cotações Combinadas (Exemplos, podemos adicionar mais depois)
    cotacao_milhar_centena = models.DecimalField("Milhar/Centena (4400x)", max_digits=7, decimal_places=2, default=4400.0)
    
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
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='apostas')
    sorteio = models.ForeignKey(Sorteio, on_delete=models.PROTECT, related_name='apostas')
    
    tipo_jogo = models.CharField(max_length=3, choices=TIPOS_JOGO)
    valor = models.DecimalField(max_digits=10, decimal_places=2) # Quanto o usuário apostou
    
    # O palpite (Pode ser o número do grupo "16" ou a milhar "1234")
    palpite = models.CharField(max_length=50)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    ganhou = models.BooleanField(default=False)
    valor_premio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.usuario} - {self.get_tipo_jogo_display()} - {self.palpite}"
    

    def calcular_premio_estimado(self):
        """
        Consulta o Singleton ParametrosDoJogo para saber quanto pagar.
        """
        config = ParametrosDoJogo.load() 
        multiplicador = 0
        
        # Mapeia o tipo de jogo para o campo da config
        if self.tipo_jogo == 'G': multiplicador = config.cotacao_grupo
        elif self.tipo_jogo == 'D': multiplicador = config.cotacao_dezena
        elif self.tipo_jogo == 'C': multiplicador = config.cotacao_centena
        elif self.tipo_jogo == 'M': multiplicador = config.cotacao_milhar
        elif self.tipo_jogo == 'MC': multiplicador = config.cotacao_milhar_centena
            
        premio = self.valor * multiplicador
        
        # Aplica o teto máximo
        if premio > config.premio_maximo_aposta:
            premio = config.premio_maximo_aposta
            
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
        """
        Lógica matemática para validar se ganhou (Focada no 1º Prêmio/Cabeça).
        """
        if not self.sorteio or not self.sorteio.premio_1:
            return False 

        palpite = str(self.palpite).strip()
        resultado = str(self.sorteio.premio_1).strip()

        if self.tipo_jogo == 'M': # Milhar
            return palpite == resultado
        elif self.tipo_jogo == 'C': # Centena
            return resultado.endswith(palpite)
        elif self.tipo_jogo == 'D': # Dezena
            return resultado.endswith(palpite)
        elif self.tipo_jogo == 'G': # Grupo
            grupo_sorteado = self.descobrir_grupo(resultado)
            return int(palpite) == grupo_sorteado
        elif self.tipo_jogo == 'MC': # Milhar e Centena
             return palpite == resultado or resultado.endswith(palpite[1:])
            
        return False