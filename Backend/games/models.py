from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .utils import DEFAULT_COTACAO_LOTINHA, DEFAULT_COTACAO_QUININHA, DEFAULT_COTACAO_SENINHA


def get_default_quininha():
    return DEFAULT_COTACAO_QUININHA


def get_default_seninha():
    return DEFAULT_COTACAO_SENINHA


def get_default_lotinha():
    return DEFAULT_COTACAO_LOTINHA


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

    ativa_apostas = models.BooleanField(default=True)
    milhar_brinde_ativa = models.BooleanField(default=False)
    valor_minimo_para_brinde = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))


# Enum do Diagrama para Jogos
class JogoTipo(models.TextChoices):
    LOTERIAS = 'loterias', 'Loterias'
    BICHO = 'bicho', 'Bicho'
    LOTO = 'loto', 'Loto'


# Enum do Diagrama para Status da Aposta
class ApostaStatus(models.TextChoices):
    PENDENTE = 'pendente', 'Pendente'
    SORTEADO = 'sorteado', 'Sorteado'


class Jogo(models.Model):
    # Diagrama: id, nome, tipo
    nome = models.CharField(max_length=100)
    tipo = models.CharField(
        max_length=20,
        choices=JogoTipo.choices,
        default=JogoTipo.BICHO
    )

    # ... Manter campos úteis não listados no diagrama (active, created_at) ...
    ativo = models.BooleanField(default=True)

    def __str__(self): return self.nome


class Modalidade(models.Model):
    # Diagrama: id, jogo_id, nome, quantidade_palpites, cotacao
    jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE, related_name='modalidades')
    nome = models.CharField(max_length=100)
    quantidade_palpites = models.IntegerField(default=1, help_text="Qtd números")
    cotacao = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self): return f"{self.jogo.nome} - {self.nome}"


class Colocacao(models.Model):

    # ALINHAMENTO CRÍTICO COM DIAGRAMA
    # Diagrama: id, nome, created_at, cotacao, mascara, jogo_id, modalidade_id

    nome = models.CharField(max_length=50)  # Ex: 1º ao 5º
    cotacao = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cotação específica desta colocação")
    mascara = models.CharField(max_length=100, blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    # Relacionamentos explícitos do diagrama
    jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE, related_name='colocacoes')
    modalidade = models.ForeignKey(Modalidade, on_delete=models.CASCADE, related_name='colocacoes')

    def __str__(self): return f"{self.nome} ({self.modalidade.nome})"

    def clean(self):
        # Regra de QA: Garantir integridade da redundância do diagrama
        # Se a modalidade não pertence ao mesmo jogo informados, erro.
        if self.modalidade_id and self.jogo_id:
            if self.modalidade.jogo_id != self.jogo_id:
                raise ValidationError("A modalidade selecionada não pertence ao jogo informado.")

    def save(self, *args, **kwargs):
        # Força validação antes de salvar para manter redundância do diagrama
        self.full_clean()
        super().save(*args, **kwargs)


# Mantendo Sorteio pois é vital para o sistema funcionar, mesmo que o diagrama simplifique
class Sorteio(models.Model):
    data = models.DateField(help_text="Data do sorteio")
    horario = models.CharField(max_length=20, blank=True, null=True)
    fechado = models.BooleanField(default=False)

    premio_1 = models.CharField(max_length=10, blank=True, null=True)
    premio_2 = models.CharField(max_length=10, blank=True, null=True)
    premio_3 = models.CharField(max_length=10, blank=True, null=True)
    premio_4 = models.CharField(max_length=10, blank=True, null=True)
    premio_5 = models.CharField(max_length=10, blank=True, null=True)

    resultado = models.JSONField(blank=True, null=True, help_text="Resultado bruto (JSON)")


    def __str__(self):
        return f"{self.data}"


class Aposta(models.Model):

    # Diagrama: palpite_aposta

    # Diagrama: usuario_id
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='apostas')

    jogo = models.ForeignKey(Jogo, on_delete=models.PROTECT, null=True, blank=True, related_name='apostas')
    modalidade = models.ForeignKey(Modalidade, on_delete=models.PROTECT, null=True, blank=True, related_name='apostas')

    # Diagrama: colocacao_id (usamos `tipo_jogo` para identificar o jogo)
    colocacao = models.ForeignKey(Colocacao, on_delete=models.PROTECT, null=True, blank=True)

    # Diagrama: valor (valor da aposta)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    # Diagrama: palpites (json)
    # Define que o padrão é uma lista vazia para evitar nulls e facilitar uso
    palpites = models.JSONField(default=list)

    # Backward compatibility with legacy frontend payloads
    tipo_jogo = models.CharField(max_length=20, blank=True, null=True)
    palpite = models.CharField(max_length=50, blank=True, null=True)
    comissao_gerada = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    # Diagrama: status (Enum)
    status = models.CharField(
        max_length=20,
        choices=ApostaStatus.choices,
        default=ApostaStatus.PENDENTE
    )

    # Manter relacionamento técnico com Sorteio para apuração
    sorteio = models.ForeignKey(Sorteio, on_delete=models.PROTECT, related_name='apostas')

    criado_em = models.DateTimeField(auto_now_add=True)

    # Campos de sistema não desenhados mas necessários
    ganhou = models.BooleanField(default=False)
    valor_premio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        db_table = 'palpite_aposta' # Força o nome da tabela conforme diagrama