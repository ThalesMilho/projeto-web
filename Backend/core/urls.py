from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuração visual da Documentação
schema_view = get_schema_view(
   openapi.Info(
      title="API Jogo do Bicho",
      default_version='v1',
      description="Documentação oficial da API. Teste as rotas aqui.",
      contact=openapi.Contact(email="thales@banca.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/games/', include('games.urls')),
    
    # Rotas da Documentação (Swagger)
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]