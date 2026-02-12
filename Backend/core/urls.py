# Backend/core/urls.py

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from drf_spectacular.openapi import AutoSchema
from rest_framework.permissions import AllowAny
from django.conf import settings

# Zero Trust: Dynamic admin path from environment
admin_url = getattr(settings, 'ADMIN_URL', 'admin-secret-2024')

# Custom schema view that allows public access
class PublicSchemaView(SpectacularAPIView):
    permission_classes = [AllowAny]
    schema_class = AutoSchema

# Custom documentation views that allow public access
class PublicSwaggerView(SpectacularSwaggerView):
    permission_classes = [AllowAny]

class PublicRedocView(SpectacularRedocView):
    permission_classes = [AllowAny]

urlpatterns = [
    # 1. Painel Administrativo do Django (Obfuscated Path)
    path(f'{admin_url}/', admin.site.urls),
    
    # 2. Rotas da sua API (Accounts e Games)
    path('api/accounts/', include('accounts.urls')),
    path('api/games/', include('games.urls')),
    
    # 3. DOCUMENTAÇÃO PÚBLICA (DRF-SPECTACULAR)
    # Gera o arquivo JSON que descreve sua API (acesso público)
    path('api/schema/', PublicSchemaView.as_view(), name='schema'),
    
    # Interface visual do Swagger (acesso público)
    path('api/docs/', PublicSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Interface alternativa (Redoc) (acesso público)
    path('api/redoc/', PublicRedocView.as_view(url_name='schema'), name='redoc'),
]