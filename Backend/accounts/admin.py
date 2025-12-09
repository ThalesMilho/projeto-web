from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('cpf_cnpj', 'nome_completo', 'email', 'saldo', 'is_staff')
    
    # ADICIONA ISTO:
    search_fields = ('cpf_cnpj', 'nome_completo', 'email')
    list_filter = ('is_staff', 'is_active') # Filtros laterais úteis
    
    ordering = ('cpf_cnpj',)
      
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Pessoais', {'fields': ('cpf_cnpj', 'nome_completo', 'phone', 'saldo')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Pessoais', {'fields': ('cpf_cnpj', 'nome_completo', 'phone')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)