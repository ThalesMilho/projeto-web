# Backend/core/urls.py

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# NOTA: Não precisamos mais definir 'schema_view' aqui. 
# O drf-spectacular pega as configurações automaticamente do settings.py.

urlpatterns = [
    # 1. Painel Administrativo do Django
    path('admin/', admin.site.urls),
    
    # 2. Rotas da sua API (Accounts e Games)
    path('api/accounts/', include('accounts.urls')),
    path('api/games/', include('games.urls')),
    
    # 3. DOCUMENTAÇÃO NOVA (DRF-SPECTACULAR)
    # Gera o arquivo JSON que descreve sua API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Interface visual do Swagger (Acesse esta!)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Interface alternativa (Redoc)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]