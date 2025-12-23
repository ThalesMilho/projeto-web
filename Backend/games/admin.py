from django.contrib import admin
from django.utils.html import format_html
from .models import Bicho, Sorteio, Aposta

@admin.register(Sorteio)
class SorteioAdmin(admin.ModelAdmin):
    list_display = ('data', 'horario', 'fechado', 'premio_1')
    list_filter = ('data', 'fechado')
    ordering = ('-data',)

@admin.register(Aposta)
class ApostaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'tipo_jogo', 'valor', 'ganhou', 'ver_bilhete')
    list_filter = ('ganhou', 'tipo_jogo')
    
    def ver_bilhete(self, obj):
        return format_html(
            '<a class="button" href="/api/games/comprovante/{}/" target="_blank">🖨️ Imprimir</a>',
            obj.id
        )
    ver_bilhete.short_description = 'Comprovante'