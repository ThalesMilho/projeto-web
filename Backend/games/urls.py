from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    BichosView, 
    CotacaoView, 
    SorteiosAbertosView, 
    ApostaViewSet,       
    ApuracaoAPIView,     
    comprovante_view,
    QuininhaView,
    SeninhaView,
    LotinhaView
)

# O Router cria as rotas automáticas para o CRUD de apostas
router = DefaultRouter()
router.register(r'apostas', ApostaViewSet, basename='apostas')

urlpatterns = [
    # --- ENDPOINTS DE DADOS (Públicos) ---
    path('bichos/', BichosView.as_view(), name='lista-bichos'),
    path('cotacoes/', CotacaoView.as_view(), name='lista-cotacoes'),
    path('sorteios/abertos/', SorteiosAbertosView.as_view(), name='sorteios-abertos'),

    # --- ENDPOINTS DE REGRAS (Novos) ---
    path('quininha/', QuininhaView.as_view(), name='quininha'),
    path('seninha/', SeninhaView.as_view(), name='seninha'),
    path('lotinha/', LotinhaView.as_view(), name='lotinha'),

    # --- ENDPOINTS DE AÇÃO ---
    path('', include(router.urls)),

    # --- APURAÇÃO (Admin) ---
    path('apurar/<int:pk>/', ApuracaoAPIView.as_view(), name='apurar-sorteio'),

    # --- VISUAL (Impressão) ---
    path('comprovante/<int:pk>/', comprovante_view, name='imprimir-comprovante'),
]