from django.db import models
from django.conf import settings # Para pegar o seu CustomUser

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

# 3. A Aposta (O Ticket)
class Aposta(models.Model):
    TIPOS_JOGO = [
        ('G', 'Grupo'),           # Apostar no bicho (ex: Leão)
        ('D', 'Dezena'),          # Apostar na dezena (ex: 62)
        ('C', 'Centena'),         # Apostar na centena (ex: 162)
        ('M', 'Milhar'),          # Apostar na milhar (ex: 8162)
        ('MC', 'Milhar/Centena'), # Aposta combinada
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='apostas')
    sorteio = models.ForeignKey(Sorteio, on_delete=models.PROTECT, related_name='apostas')
    
    tipo_jogo = models.CharField(max_length=2, choices=TIPOS_JOGO)
    valor = models.DecimalField(max_digits=10, decimal_places=2) # Quanto o usuário apostou
    
    # O palpite (Pode ser o número do grupo "16" ou a milhar "1234")
    palpite = models.CharField(max_length=4) 
    
    criado_em = models.DateTimeField(auto_now_add=True)
    ganhou = models.BooleanField(default=False)
    valor_premio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.usuario} - {self.get_tipo_jogo_display()} - {self.palpite}"