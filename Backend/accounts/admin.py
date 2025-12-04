from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('cpf_cnpj', 'nome_completo', 'email', 'is_staff')
    ordering = ('cpf_cnpj',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Pessoais', {'fields': ('cpf_cnpj', 'nome_completo', 'phone', 'bio')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Pessoais', {'fields': ('cpf_cnpj', 'nome_completo', 'phone')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)