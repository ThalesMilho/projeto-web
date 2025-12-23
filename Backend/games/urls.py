from django.urls import path
from .views import (
    BichosView, 
    CotacaoView, 
    SorteiosAbertosView, 
    QuininhaView, 
    SeninhaView,  
    LotinhaView,
    RealizarApostaView,
    ApuracaoView
)

urlpatterns = [
    path('bichos/', BichosView.as_view(), name='bichos'),
    path('cotacao/', CotacaoView.as_view(), name='cotacao'),
    path('sorteios-abertos/', SorteiosAbertosView.as_view(), name='sorteios-abertos'),
    path('quininha/', QuininhaView.as_view(), name='quininha'),   
    path('seninha/', SeninhaView.as_view(), name='seninha'),     
    path('lotinha/', LotinhaView.as_view(), name='lotinha'),
    path('apostar/', RealizarApostaView.as_view(), name='realizar-aposta'),
    path('apurar/<int:pk>/', ApuracaoView.as_view(), name='apurar-sorteio'),
]