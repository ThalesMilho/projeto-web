from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # Atualizado para refletir o diagrama
    # 1. Mude 'documento' -> 'cpf_cnpj' e 'nome' -> 'nome_completo'
    list_display = ('cpf_cnpj', 'nome_completo', 'email', 'saldo', 'recebeu_bonus', 'is_staff')
    
    # 2. Atualize a busca também
    search_fields = ('cpf_cnpj', 'nome_completo', 'email')
    list_filter = ('tipo_usuario', 'is_staff', 'conta_suspeita')

    # 3. Corrija a ordenação
    ordering = ('cpf_cnpj',)

    fieldsets = UserAdmin.fieldsets + (
        ('Informações Pessoais', {'fields': ('nome_completo', 'cpf_cnpj', 'phone', 'saldo')}),
        ('Sistema de Bônus & Rollover', {
            'fields': ('recebeu_bonus', 'meta_rollover', 'total_apostado_rollover'),
            'classes': ('collapse',),
        }),
        ('Afiliados e Gerentes', {
            'fields': ('afiliado', 'gerente', 'comissao_percentual', 'modo_comissao'),
        }),
        ('Segurança e Compliance', {
            'fields': ('conta_suspeita', 'motivo_suspeita', 'ip_registro', 'ultimo_ip', 'data_primeiro_deposito'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Pessoais', {'fields': ('nome_completo', 'cpf_cnpj', 'phone')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)