from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # Adicionei 'recebeu_bonus' e 'saldo' na lista geral para facilitar a visualização
    list_display = ('cpf_cnpj', 'nome_completo', 'email', 'saldo', 'recebeu_bonus', 'is_staff')
    
    search_fields = ('cpf_cnpj', 'nome_completo', 'email')
    list_filter = ('is_staff', 'is_active', 'recebeu_bonus') 
    
    ordering = ('cpf_cnpj',)
      
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Pessoais', {'fields': ('cpf_cnpj', 'nome_completo', 'phone', 'saldo')}),
        # --- NOVO BLOCO: ADICIONE ISTO ---
        ('Sistema de Bônus & Rollover', {
            'fields': ('recebeu_bonus', 'meta_rollover', 'total_apostado_rollover'),
            'classes': ('collapse',), # Opcional: deixa o menu minimizável
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Pessoais', {'fields': ('cpf_cnpj', 'nome_completo', 'phone')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)