from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

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
    nome_completo = models.CharField(max_length=255, verbose_name="Nome Completo")
    cpf_cnpj = models.CharField(max_length=14, unique=True, verbose_name="CPF ou CNPJ")
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="WhatsApp")
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Saldo em Conta")
    
    # --- SISTEMA DE BÔNUS ---
    recebeu_bonus = models.BooleanField(default=False)
    meta_rollover = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_apostado_rollover = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # Configurações do Django
    username = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    USERNAME_FIELD = 'cpf_cnpj'
    REQUIRED_FIELDS = ['email', 'nome_completo']

    objects = CustomUserManager()

    def __str__(self):
        return self.cpf_cnpj

    def pode_sacar(self):
        if self.meta_rollover <= 0: return True
        return self.total_apostado_rollover >= self.meta_rollover

    # --- A FUNÇÃO QUE FALTAVA ---
    def quanto_falta_rollover(self):
        """Retorna quanto falta apostar para liberar o saque"""
        falta = self.meta_rollover - self.total_apostado_rollover
        return falta if falta > 0 else 0
    
class Transacao(models.Model):
    TIPO_CHOICES = [
        ('APOSTA', 'Débito - Aposta'),
        ('PREMIO', 'Crédito - Prêmio'),
        ('DEPOSITO', 'Crédito - Depósito'),
        ('SAQUE', 'Débito - Saque'),
        ('ESTORNO', 'Crédito - Estorno'),
    ]
    
    usuario = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='extrato')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=12, decimal_places=2) # Valor da movimentação
    
    # Snapshot do saldo: CRUCIAL para auditoria. 
    # Permite reconstruir a história e ver se bate com o saldo atual.
    saldo_anterior = models.DecimalField(max_digits=12, decimal_places=2) 
    saldo_posterior = models.DecimalField(max_digits=12, decimal_places=2)
    
    data = models.DateTimeField(auto_now_add=True)
    descricao = models.CharField(max_length=255, blank=True, null=True) # Ex: "Aposta #123 (Milhar)"

    def __str__(self):
        return f"{self.data} - {self.usuario} - {self.tipo} - R$ {self.valor}"