from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from decimal import Decimal 

class CustomUserManager(BaseUserManager):
    """
    Gerenciador customizado para fazer o CPF/CNPJ ser o identificador único
    ao invés do username.
    """
    use_in_migrations = True

    def _create_user(self, cpf_cnpj, password, **extra_fields):
        if not cpf_cnpj:
            raise ValueError('O CPF/CNPJ é obrigatório')

        extra_fields.setdefault('username', cpf_cnpj)

        # AQUI ESTAVA O ERRO: mudamos de 'documento' para 'cpf_cnpj'
        user = self.model(cpf_cnpj=cpf_cnpj, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, cpf_cnpj, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(cpf_cnpj, password, **extra_fields)

    def create_superuser(self, cpf_cnpj, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser precisa ter is_superuser=True.')

        return self._create_user(cpf_cnpj, password, **extra_fields)


class CustomUser(AbstractUser):
    # ALINHAMENTO COM DIAGRAMA: usuarios
    # Nome completo visível no sistema
    nome_completo = models.CharField(max_length=255, verbose_name="Nome Completo")
    # CPF/CNPJ usado como identificador único
    cpf_cnpj = models.CharField(max_length=14, unique=True, verbose_name="CPF ou CNPJ")
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="WhatsApp")
    # saldo = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Saldo em Conta")    
    saldo = models.BigIntegerField(default=0, verbose_name="Saldo em Conta (Centavos)")    
    # --- SISTEMA DE BÔNUS ---
    recebeu_bonus = models.BooleanField(default=False)
    meta_rollover = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_apostado_rollover = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))


    # --- NOVOS CAMPOS: Segurança e Compliance ---
    ip_registro = models.GenericIPAddressField(null=True, blank=True)
    ultimo_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # FTD Real: Armazena a data exata do 1º depósito aprovado para KPI preciso
    data_primeiro_deposito = models.DateTimeField(null=True, blank=True, db_index=True)
    
    # Risco: Marcação para usuários perigosos (fraudadores/bônus abusers)
    conta_suspeita = models.BooleanField(default=False)
    motivo_suspeita = models.TextField(blank=True, null=True)

    TIPOS_USUARIO = (
        ('JOGADOR', 'Jogador Comum'),
        ('AFILIADO', 'Afiliado'), 
        ('ADMIN', 'Administrador'),
    )
    tipo_usuario = models.CharField(max_length=10, choices=TIPOS_USUARIO, default='JOGADOR')
    
    # Porcentagem de comissão (Ex: 15.00 para 15%)
    comissao_percentual = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    MODO_COMISSAO_CHOICES = [
        ('APOSTA', 'Ganha % por Aposta Feita'),
        ('DEPOSITO', 'Ganha % por Depósito Realizado'),
    ]
    modo_comissao = models.CharField(
        max_length=10, 
        choices=MODO_COMISSAO_CHOICES, 
        default='APOSTA',
        verbose_name="Modo de Comissão"
    )

    # Diagrama: afiliado_id (usuarios)
    afiliado = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='indicados',
        db_column='afiliado_id' # Força o nome da coluna no banco
    )

    # Opcional: Se o cambista tiver um gerente acima dele
    gerente = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinados')



    # Configurações do Django
    username = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    # Mapeamento para manter compatibilidade com Django Auth
    USERNAME_FIELD = 'cpf_cnpj'  # Importante: não pode ser 'documento'
    REQUIRED_FIELDS = ['email', 'nome_completo']

    objects = CustomUserManager()

    def __str__(self):
        return self.cpf_cnpj

    def pode_sacar(self):
        if self.meta_rollover <= Decimal('0.00'): return True
        return self.total_apostado_rollover >= self.meta_rollover

    def quanto_falta_rollover(self):
        """Retorna quanto falta apostar para liberar o saque"""
        falta = self.meta_rollover - self.total_apostado_rollover
        return falta if falta > 0 else 0
    def aplicar_bonus_deposito(self, valor_deposito):

        bonus = Decimal('0.00')
        if not self.recebeu_bonus:
            teto_bonus = Decimal('500.00')
            bonus = valor_deposito if valor_deposito <= teto_bonus else teto_bonus
            self.recebeu_bonus = True
            base_calculo = valor_deposito + bonus
            acrescimo_rollover = base_calculo * 2
            self.meta_rollover += acrescimo_rollover
        return bonus
    def processar_comissao(self, valor_base, evento_origem):
        """
        Calcula e paga a comissão ao padrinho (se houver).
        valor_base: Valor da aposta ou do depósito (Decimal)
        evento_origem: 'APOSTA' ou 'DEPOSITO' (String)
        """
        # 1. Tem indicação? O promotor existe?
        promotor = self.afiliado
        if not promotor:
            return False # Ninguém para receber

        # 2. O promotor está configurado para ganhar nesse tipo de evento?
        # Ex: Se o promotor ganha por 'DEPOSITO' mas o evento é 'APOSTA', ele não ganha nada.
        if promotor.modo_comissao != evento_origem:
            return False

        # 3. O percentual é válido?
        if promotor.comissao_percentual <= 0:
            return False

        # 4. Cálculos Financeiros (Com segurança Decimal)
        valor_base = Decimal(str(valor_base))
        porcentagem = promotor.comissao_percentual / Decimal('100.00')
        valor_comissao = valor_base * porcentagem
        
        # Arredonda para 2 casas (centavos) para baixo
        from decimal import ROUND_DOWN
        valor_comissao = valor_comissao.quantize(Decimal('0.01'), rounding=ROUND_DOWN)

        if valor_comissao <= 0:
            return False

        # 5. Paga o Promotor
        saldo_antes = promotor.saldo
        promotor.saldo += valor_comissao
        promotor.save()

        # 6. Gera o Extrato (Auditabilidade)
        # Usamos 'promotor.extrato' porque definimos related_name='extrato' na model Transacao
        promotor.extrato.create(
            usuario=promotor,
            tipo='COMISSAO',
            valor=valor_comissao,
            saldo_anterior=saldo_antes,
            saldo_posterior=promotor.saldo,
            descricao=f"Comissão sobre {evento_origem} de {self.nome_completo or self.cpf_cnpj}"
        )

        return True


class SolicitacaoPagamento(models.Model):
    TIPO_CHOICES = [
        ('DEPOSITO', 'Depósito'),
        ('SAQUE', 'Saque'),
    ]
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('APROVADO', 'Aprovado'),
        ('RECUSADO', 'Recusado/Falhou'),
        ('CANCELADO', 'Cancelado'),
        ('EM_ANALISE', 'Em Análise (Compliance)'), 
        ('PROCESSANDO', 'Processando Pagamento'),
    ]

    usuario = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='solicitacoes')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    valor = models.BigIntegerField(verbose_name="Valor (Centavos)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    
    # Integração com Fintech (SkalePay)
    id_externo = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name="ID da Transação na SkalePay")
    qr_code = models.TextField(null=True, blank=True) 
    qr_code_url = models.URLField(null=True, blank=True)
    # Chave Pix usada para saques (ou depósitos com identificação do recebedor)
    chave_pix = models.CharField(max_length=255, null=True, blank=True, verbose_name="Chave Pix")
    

    # --- COMPLIANCE E AUDITORIA ---
    risco_score = models.IntegerField(default=0, help_text="0-100. Acima de 80 bloqueia auto.")
    analise_motivo = models.TextField(blank=True, null=True, help_text="Motivo da análise de risco")
    data_aprovacao = models.DateTimeField(null=True, blank=True)


    # Auditoria e Controle
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    aprovado_por = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='aprovacoes_financeiras')

    def __str__(self):
        return f"{self.tipo} - {self.usuario} - {self.get_status_display()} - R$ {self.valor}"

# --- NOVO MODELO: ETL / DASHBOARD OTIMIZADO ---
# Em Backend/accounts/models.py

class MetricasDiarias(models.Model):
    """
    Tabela consolidada. Cada linha aqui é um dia fechado.
    Permite gráficos instantâneos sem varrer milhões de transações.
    """
    data = models.DateField(unique=True, db_index=True)
    
    # 1. Financeiro (Caixa) - Detalhado por Valor e Quantidade
    total_deposito_valor = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_deposito_qtd = models.IntegerField(default=0)
    
    total_saque_valor = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_saque_qtd = models.IntegerField(default=0)
    
    total_bonus_concedido = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))

    # 2. Operacional (Apostas)
    total_apostado = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_premios = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    house_edge_valor = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name="Lucro Bruto (GGR)")
    
    # 3. KPIs de Crescimento
    novos_usuarios = models.IntegerField(default=0)
    usuarios_ativos = models.IntegerField(default=0)
    
    # FTDs Reais (First Time Deposits)
    ftds_qtd = models.IntegerField(default=0, verbose_name="Qtd Primeiros Depósitos")
    ftds_valor = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # 4. JSON para Flexibilidade (Ex: Top Modalidades)
    performance_modalidades = models.JSONField(default=dict, blank=True)
    # JSON para guardar: {"00h": 500, "01h": 200... "23h": 1500}
    mapa_calor_horas = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = "Métrica Diária"
        verbose_name_plural = "Métricas Diárias"
        get_latest_by = 'data'

class Transacao(models.Model):
    TIPO_CHOICES = [
        ('APOSTA', 'Débito - Aposta'),
        ('PREMIO', 'Crédito - Prêmio'),
        ('DEPOSITO', 'Crédito - Depósito'),
        ('SAQUE', 'Débito - Saque'),
        ('ESTORNO', 'Crédito - Estorno'),
        ('BONUS', 'Crédito - Bônus'),
        ('COMISSAO', 'Crédito - Comissão'),
    ]
    
    origem_solicitacao = models.ForeignKey(
        SolicitacaoPagamento,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='transacoes'
    )
    usuario = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='extrato')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    valor = models.BigIntegerField(verbose_name="Valor (Centavos)")
    
    # Snapshot do saldo: CRUCIAL para auditoria. 
    # Permite reconstruir a história e ver se bate com o saldo atual.
    saldo_anterior = models.BigIntegerField(verbose_name="Saldo Anterior (Centavos)")
    saldo_posterior = models.BigIntegerField(verbose_name="Saldo Posterior (Centavos)")
    
    data = models.DateTimeField(auto_now_add=True)
    descricao = models.CharField(max_length=255, blank=True, null=True) # Ex: "Aposta #123 (Milhar)"

    def __str__(self):
        return f"{self.data} - {self.usuario} - {self.tipo} - R$ {self.valor}"
    
    @property
    def nome_completo(self):
        return self.usuario.nome_completo
        
    @property
    def cpf_cnpj(self):
        return self.usuario.cpf_cnpj