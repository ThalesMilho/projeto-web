from django.urls import path
from .views import RegisterView, CustomLoginView 
from rest_framework_simplejwt.views import TokenRefreshView
from .views import DashboardFinanceiroView 
from .views import SimularDepositoView, SolicitarSaqueView 
from .views import SkalePayWebhookView 

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('simular-deposito/', SimularDepositoView.as_view(), name='simular-deposito'),
    
    path('login/', CustomLoginView.as_view(), name='login'),
    
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dashboard/', DashboardFinanceiroView.as_view(), name='dashboard-admin'),
    path('simular-deposito/', SimularDepositoView.as_view(), name='simular-deposito'),
    path('saque/', SolicitarSaqueView.as_view(), name='solicitar-saque'), 
    
    path('webhook/skalepay/', SkalePayWebhookView.as_view(), name='webhook-skalepay'),
]