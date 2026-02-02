from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from decimal import Decimal
from .models import CustomUser, SolicitacaoPagamento #
import json
import hmac
import hashlib
from django.test import override_settings

class AccountsTests(TestCase):
    def test_criar_usuario_com_cpf(self):
        """
        Teste se o CustomUserManager cria o usuário corretamente
        usando o CPF como identificador.
        """
        User = get_user_model()
        cpf = "12345678900"
        senha = "senha_segura_123"
        
        # Criação
        user = User.objects.create_user(
            cpf_cnpj=cpf, 
            password=senha, 
            nome_completo="Teste da Silva"
        )

        # Verificações
        self.assertEqual(user.cpf_cnpj, cpf)
        self.assertEqual(user.username, cpf) 
        self.assertTrue(user.check_password(senha))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(float(user.saldo), 0.00)

    def test_criar_superuser(self):
        """Teste se o Superusuário ganha as permissões certas"""
        User = get_user_model()
        admin = User.objects.create_superuser(
            cpf_cnpj="99999999999", 
            password="admin", 
            nome_completo="Admin Chefe"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

class FluxoPagamentoTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "cpf_cnpj": "11122233344",
            "password": "senha_forte_123",
            "nome_completo": "Usuario Tester"
        }
        self.user = CustomUser.objects.create_user(**self.user_data) #
        self.client.force_authenticate(user=self.user)

    # O MOCK ACONTECE AQUI
    @patch('accounts.services.requests.post') #
    def test_gerar_deposito_com_mock(self, mock_post):
        """
        Testa a geração de depósito fingindo que a API da SkalePay respondeu 200 OK.
        Não altera o banco de dados real nem chama a API de verdade.
        """
        
        # 1. Configurar a "Mentira" (O Mock)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "transacao_fake_999",
            "pixQrCode": "00020126580014br.gov.bcb.pix...QRCODE_TESTE...",
            "emv": "00020126580014br.gov.bcb.pix...QRCODE_TESTE..."
        }
        mock_post.return_value = mock_response

        # 2. Executar a Ação Real
        payload = {"valor": 50.00}
        # IMPORTANTE: Verifique se sua URL no urls.py é exatamente essa
        response = self.client.post('/api/accounts/depositar/', payload, format='json')

        # 3. Verificações
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("qr_code", response.data)
        # O sistema retorna o ID interno (int) para rastreabilidade
        self.assertIn('id_transacao', response.data)
        self.assertIsInstance(response.data['id_transacao'], int)

        # Verifica se gravou no banco de teste usando o ID interno retornado
        deposito_db = SolicitacaoPagamento.objects.get(id=response.data['id_transacao'])
        self.assertEqual(deposito_db.valor, Decimal('50.00'))
        self.assertEqual(deposito_db.status, 'PENDENTE')
    @override_settings(SKALEPAY_SECRET_KEY='chave_teste_123')
    def test_webhook_aprovacao_deposito(self):
        """
        Simula a SkalePay avisando que o Pix foi PAGO.
        Verifica se o sistema valida a assinatura e libera o saldo.
        """
        # 1. PREPARAÇÃO: Cria um pedido de depósito pendente no banco
        solicitacao = SolicitacaoPagamento.objects.create(
            usuario=self.user,
            tipo='DEPOSITO',
            valor=Decimal('100.00'),
            status='PENDENTE',
            id_externo='transacao_pix_real' # ID que simularemos vir da SkalePay
        )

        # 2. AÇÃO: Monta o Payload (JSON) que a SkalePay enviaria
        payload = {
            "transaction_id": "transacao_pix_real",
            "status": "PAID",
            "amount": 100.00,
            "customer_custom_id": self.user.id
        }
        payload_json = json.dumps(payload)

        # 3. SEGURANÇA: Gera a Assinatura (HMAC SHA256) com a chave de teste
        # Isso prova que o backend só aceita quem tem a chave certa
        secret = b'chave_teste_123'
        signature = hmac.new(secret, payload_json.encode('utf-8'), hashlib.sha256).hexdigest()

        # 4. EXECUÇÃO: Dispara o Webhook contra a nossa API
        response = self.client.post(
            '/api/accounts/webhook/skalepay/', 
            data=payload, 
            content_type='application/json',
            headers={'X-SkalePay-Signature': signature}
        )

        # 5. VERIFICAÇÃO: Ocorreu tudo bem?
        self.assertEqual(response.status_code, 200) 

        # O saldo caiu na conta?
        self.user.refresh_from_db()
        self.assertEqual(self.user.saldo, Decimal('200.00')) 
        
        # O status do pedido mudou para APROVADO?
        solicitacao.refresh_from_db()
        self.assertEqual(solicitacao.status, 'APROVADO')

    @patch('accounts.services.requests.post')
    def test_saque_fluxo_completo(self, mock_post):
        """
        Testa se o usuário consegue sacar quando tem saldo livre.
        Verifica se o saldo é descontado corretamente.
        """
        # 1. PREPARAÇÃO: Dar dinheiro para o usuário manualmente
        # (Não usamos a API de depósito aqui para evitar travas de Rollover/Bônus neste teste específico)
        self.user.saldo = Decimal('500.00')
        self.user.save()

        # 2. MOCK: Fingir que a SkalePay aceitou e pagou o Pix
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "saque_sucesso_123",
            "status": "COMPLETED" 
        }
        mock_post.return_value = mock_response

        # 3. AÇÃO: Usuário pede saque de R$ 100,00
        payload = {
            "valor": 100.00,
            "chave_pix": "minha@chave.pix"
        }
        response = self.client.post('/api/accounts/saque/', payload, format='json')

        # 4. VERIFICAÇÃO
        self.assertEqual(response.status_code, 200) # Deve dar sucesso
        
        # O saldo caiu de 500 para 400?
        self.user.refresh_from_db()
        self.assertEqual(self.user.saldo, Decimal('400.00')) 
        
        # Ficou registrado no histórico?
        saque = SolicitacaoPagamento.objects.get(id_externo="saque_sucesso_123")
        self.assertEqual(saque.status, 'APROVADO')

    @patch('accounts.services.requests.post')
    def test_saque_fluxo_completo(self, mock_post):
        """
        Testa se o usuário consegue sacar quando tem saldo livre.
        Verifica se o saldo é descontado corretamente.
        """
        # 1. PREPARAÇÃO: Dar dinheiro para o usuário manualmente
        # (Não usamos o fluxo de depósito aqui para evitar travas de Rollover/Bônus neste teste específico)
        self.user.saldo = Decimal('500.00')
        self.user.save()

        # 2. MOCK: Fingir que a SkalePay aceitou e pagou o Pix
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "saque_sucesso_123",
            "status": "COMPLETED" 
        }
        mock_post.return_value = mock_response

        # 3. AÇÃO: Usuário pede saque de R$ 100,00
        payload = {
            "valor": 100.00,
            "chave_pix": "minha@chave.pix"
        }
        # Verifica a URL correta no seu urls.py (pode ser /api/accounts/saque/ ou /solicitar-saque/)
        response = self.client.post('/api/accounts/saque/', payload, format='json')

        # 4. VERIFICAÇÃO
        self.assertEqual(response.status_code, 200) # Deve dar sucesso
        
        # O saldo caiu de 500 para 400?
        self.user.refresh_from_db()
        self.assertEqual(self.user.saldo, Decimal('400.00')) 
        
        # Ficou registrado no histórico?
        saque = SolicitacaoPagamento.objects.get(id_externo="saque_sucesso_123")
        self.assertEqual(saque.status, 'APROVADO')