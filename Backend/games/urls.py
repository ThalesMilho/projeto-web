from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importa apenas as views que estamos usando no momento
from .views import (
    BichosView, 
    CotacaoView, 
    SorteiosAbertosView, 
    ApostaViewSet,       # Nova ViewSet (Cria e Lista)
    ApuracaoAPIView,     # Opcional (Apuração via API)
    comprovante_view     # Visual para impressão
)

# O Router cria as rotas automáticas para o CRUD de apostas
router = DefaultRouter()
router.register(r'apostas', ApostaViewSet, basename='apostas')

urlpatterns = [
    # --- ENDPOINTS DE DADOS (Para preencher o menu do site) ---
    path('bichos/', BichosView.as_view(), name='lista-bichos'),
    path('cotacoes/', CotacaoView.as_view(), name='lista-cotacoes'), # <--- Sua lista gigante está aqui
    path('sorteios/abertos/', SorteiosAbertosView.as_view(), name='sorteios-abertos'),

    # --- ENDPOINTS DE AÇÃO ---
    # Substitui o antigo 'apostar/' pelo router que faz tudo (cria e lista)
    path('', include(router.urls)),

    # --- APURAÇÃO (Backup caso não queira usar o Admin) ---
    path('apurar/<int:pk>/', ApuracaoAPIView.as_view(), name='apurar-sorteio'),

    # --- VISUAL (Impressão) ---
    path('comprovante/<int:pk>/', comprovante_view, name='imprimir-comprovante'),
]