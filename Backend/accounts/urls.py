from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, 
    CustomLoginView, 
    UserProfileView,          
    DashboardFinanceiroView, 
    GerarDepositoPixView, 
    SolicitarSaqueView, 
    SkalePayWebhookView,
    BackofficeSolicitacaoViewSet, 
    RiscoComplianceViewSet, 
    HistoricoUsuarioView, 
    PasswordResetView, 
    PasswordResetConfirmView,
    RelatoriosOperacionaisView,
    RelatorioFinanceiroView,
    testar_conexao_skalepay,
)

# Router
router = DefaultRouter()
# Mudei de 'transacoes' para 'solicitacoes' para bater com o QA Script e o padrão REST
router.register(r'backoffice/solicitacoes', BackofficeSolicitacaoViewSet, basename='admin-solicitacoes')
router.register(r'backoffice/risco', RiscoComplianceViewSet, basename='admin-risco')
router.register(r'meus-movimentos', HistoricoUsuarioView, basename='user-historico')

urlpatterns = [
    # Autenticação
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # --- PERFIL (CRUCIAL PARA O TESTE QA) ---
    # Essa rota permite ao front pegar nome e SALDO do usuário logado
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('test-skalepay/', testar_conexao_skalepay, name='test-skalepay'),
    # Senha
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    # Dashboards Admin
    path('dashboard/', DashboardFinanceiroView.as_view(), name='dashboard-admin'),
    path('relatorios/operacional/', RelatoriosOperacionaisView.as_view(), name='relatorios-ops'),
    path('relatorios/financeiro/csv/', RelatorioFinanceiroView.as_view(), name='relatorio_csv'),

    # Financeiro (Usuário)
    path('depositar/', GerarDepositoPixView.as_view(), name='gerar-deposito'),
    path('saque/', SolicitarSaqueView.as_view(), name='solicitar-saque'), 
    
    # Webhook
    path('webhook/skalepay/', SkalePayWebhookView.as_view(), name='skalepay-webhook'),

    # Rotas do Router (Final)
    path('', include(router.urls)),
]

