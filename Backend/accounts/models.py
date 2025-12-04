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
    
    bio = models.TextField(blank=True, null=True)

    username = models.CharField(max_length=150, blank=True, null=True)
    
    email = models.EmailField(blank=True, null=True)

    USERNAME_FIELD = 'cpf_cnpj'
    REQUIRED_FIELDS = ['email', 'nome_completo']

    objects = CustomUserManager()

    def __str__(self):
        return self.cpf_cnpj