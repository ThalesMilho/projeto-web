from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html
from .models import (
    Sorteio, 
    Aposta, 
    ParametrosDoJogo, 
    Jogo, 
    Modalidade, 
    Colocacao
)

# Configuração do Título do Painel
admin.site.site_header = "Sistema do Bicho - Backoffice"
admin.site.site_title = "Admin Bicho"
admin.site.index_title = "Gestão da Banca"

# --- NOVOS MODELOS (ESSENCIAIS PARA FUNCIONAR) ---

@admin.register(Jogo)
class JogoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'ativo')
    search_fields = ('nome',)
    list_filter = ('ativo',)

@admin.register(Modalidade)
class ModalidadeAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'jogo', 'cotacao')
    search_fields = ('nome', 'jogo__nome')
    list_filter = ('jogo',)
    autocomplete_fields = ['jogo']

@admin.register(Colocacao)
class ColocacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    search_fields = ('nome',)

# --- MODELOS EXISTENTES ATUALIZADOS ---

@admin.register(ParametrosDoJogo)
class ParametrosDoJogoAdmin(admin.ModelAdmin):
    # Mantivemos apenas as configs globais, já que cotações agora são por Modalidade
    fieldsets = (
        ('Controle Geral', {
            'fields': ('ativa_apostas', 'premio_maximo_aposta')
        }),
        # Mantemos campos antigos apenas se você ainda não os removeu do Model.
        # Se removeu do model ParametrosDoJogo, apague esses grupos abaixo.
    )
    def has_add_permission(self, request):
        return not ParametrosDoJogo.objects.exists()
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Sorteio)
class SorteioAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'data', 'total_apostas', 'faturamento', 'premiacao', 'lucro_banca')
    actions = ['fechar_sorteios', 'reabrir_sorteios', 'apurar_apuracao_action']
    list_filter = ('data',)
    search_fields = ['id', 'data']
    readonly_fields = ('faturamento', 'premiacao', 'lucro_banca')
    
    # Métodos calculados
    def total_apostas(self, obj):
        return obj.apostas.count()
    total_apostas.short_description = "Qtd. Apostas"

    def faturamento(self, obj):
        total = obj.apostas.aggregate(Sum('valor'))['valor__sum'] or 0
        return f"R$ {total:.2f}"
    faturamento.short_description = "Entrada"

    def premiacao(self, obj):
        total = obj.apostas.filter(ganhou=True).aggregate(Sum('valor_premio'))['valor_premio__sum'] or 0
        return f"R$ {total:.2f}"
    premiacao.short_description = "Saída"

    def lucro_banca(self, obj):
        entrada = obj.apostas.aggregate(Sum('valor'))['valor__sum'] or 0
        saida = obj.apostas.filter(ganhou=True).aggregate(Sum('valor_premio'))['valor_premio__sum'] or 0
        lucro = entrada - saida
        cor = "green" if lucro >= 0 else "red"
        return format_html(f'<span style="color: {cor}; font-weight: bold;">R$ {lucro:.2f}</span>')
    lucro_banca.short_description = "Lucro Líquido"

    # Actions
    @admin.action(description="🔒 Fechar Sorteios")
    def fechar_sorteios(self, request, queryset):
        queryset.update(fechado=True)

    @admin.action(description="🔓 Reabrir Sorteios")
    def reabrir_sorteios(self, request, queryset):
        queryset.update(fechado=False)

    @admin.action(description="🎲 Apurar Resultados")
    def apurar_apuracao_action(self, request, queryset):
        processados = 0
        erros = 0
        for sorteio in queryset:
            # Chama o método do Model Sorteio (certifique-se que ele existe lá)
            pass

# --- APOSTA ADMIN (O MAIS CRÍTICO) ---

@admin.register(Aposta)
class ApostaAdmin(admin.ModelAdmin):
    # REMOVIDO 'jogo' (campo removido do Model). Usamos campos válidos existentes.
    list_display = ('id', 'usuario', 'tipo_jogo', 'valor', 'criado_em', 'ganhou')

    # Filtros válidos
    list_filter = ('ganhou', 'tipo_jogo', 'sorteio__data', 'criado_em')

    # Pesquisas por usuário/id/palpites
    search_fields = ('usuario__username', 'id', 'palpites')

    # Autocomplete: removido 'jogo'
    autocomplete_fields = ['usuario', 'sorteio']