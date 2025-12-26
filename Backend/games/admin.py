from django.contrib import admin
from django.db.models import Sum, Count
from django.utils.html import format_html
from .models import Bicho, Sorteio, Aposta

# Configuração do Título do Painel
admin.site.site_header = "Sistema do Bicho - Backoffice"
admin.site.site_title = "Admin Bicho"
admin.site.index_title = "Gestão da Banca"

@admin.register(Bicho)
class BichoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'nome', 'dezenas')
    search_fields = ('nome', 'dezenas')
    ordering = ('numero',)

@admin.register(Sorteio)
class SorteioAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'fechado', 'total_apostas', 'faturamento', 'premiacao', 'lucro_banca', 'status_cor')
    list_filter = ('fechado', 'horario', 'data')
    search_fields = ['id', 'data']
    actions = ['fechar_sorteios', 'reabrir_sorteios']
    readonly_fields = ('faturamento', 'premiacao', 'lucro_banca')

    # --- COLUNAS CALCULADAS (Métricas de Negócio) ---

    def total_apostas(self, obj):
        return obj.apostas.count()
    total_apostas.short_description = "Qtd. Apostas"

    def faturamento(self, obj):
        total = obj.apostas.aggregate(Sum('valor'))['valor__sum'] or 0
        return f"R$ {total:.2f}"
    faturamento.short_description = "Entrada (Cash In)"

    def premiacao(self, obj):
        total = obj.apostas.filter(ganhou=True).aggregate(Sum('valor_premio'))['valor_premio__sum'] or 0
        return f"R$ {total:.2f}"
    premiacao.short_description = "Saída (Prêmios)"

    def lucro_banca(self, obj):
        entrada = obj.apostas.aggregate(Sum('valor'))['valor__sum'] or 0
        saida = obj.apostas.filter(ganhou=True).aggregate(Sum('valor_premio'))['valor_premio__sum'] or 0
        lucro = entrada - saida
        
        cor = "green" if lucro >= 0 else "red"
        return format_html(f'<span style="color: {cor}; font-weight: bold;">R$ {lucro:.2f}</span>')
    lucro_banca.short_description = "Lucro Líquido"

    def status_cor(self, obj):
        icon = "🔒 Fechado" if obj.fechado else "🟢 Aberto"
        return icon
    status_cor.short_description = "Status"

    # --- ACTIONS (Botões de Ação em Massa) ---
    @admin.action(description="🔒 Fechar Sorteios Selecionados")
    def fechar_sorteios(self, request, queryset):
        queryset.update(fechado=True)

    @admin.action(description="🔓 Reabrir Sorteios Selecionados")
    def reabrir_sorteios(self, request, queryset):
        queryset.update(fechado=False)

@admin.register(Aposta)
class ApostaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario_info', 'detalhes_jogo', 'valor_formatado', 'status_badge', 'ver_bilhete')
    list_filter = ('ganhou', 'tipo_jogo', 'sorteio__horario', 'criado_em')
    search_fields = ('usuario__username', 'usuario__cpf_cnpj', 'id', 'palpite')
    autocomplete_fields = ['usuario', 'sorteio']

    def usuario_info(self, obj):
        return f"{obj.usuario.username} ({obj.usuario.nome_completo})"
    usuario_info.short_description = "Apostador"

    def detalhes_jogo(self, obj):
        return f"{obj.get_tipo_jogo_display()} - {obj.palpite}"
    detalhes_jogo.short_description = "Jogo"

    def valor_formatado(self, obj):
        return f"R$ {obj.valor:.2f}"
    valor_formatado.short_description = "Valor"

    def status_badge(self, obj):
        if obj.ganhou:
            return format_html('<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">🏆 GANHOU (R$ {})</span>', obj.valor_premio)
        return format_html('<span style="color: #666;">Pendente/Perdeu</span>')
    status_badge.short_description = "Resultado"

    def ver_bilhete(self, obj):
        return format_html(
            '<a class="button" href="/api/games/comprovante/{}/" target="_blank" style="font-weight:bold;">🖨️ Imprimir</a>',
            obj.id
        )
    ver_bilhete.short_description = 'Ação'