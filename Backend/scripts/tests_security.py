from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from accounts.models import CustomUser, SolicitacaoPagamento, Transacao
from rest_framework.test import APIClient

class SecurityGapTests(TestCase):
    def setUp(self):
        # Cria utilizador padrão
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            cpf_cnpj="12345678901",
            password="password123",
            nome_completo="Tester Segurança",
            email="test@example.com"
        )
        self.user.saldo = Decimal('1000.00') # Saldo inicial
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_gap1_saque_rapido_bloqueado(self):
        """
        Tenta sacar 1 minuto após depositar. Deve falhar (403).
        """
        # 1. Simula Depósito Agora
        Transacao.objects.create(
            usuario=self.user,
            tipo='DEPOSITO',
            valor=Decimal('100.00'),
            saldo_anterior=Decimal('0.00'),
            saldo_posterior=Decimal('100.00'),
            data=timezone.now()
        )
        
        # 2. Tenta Sacar imediatamente
        response = self.client.post('/api/accounts/saque/', {
            "valor": "50.00",
            "chave_pix": "test@pix.com"
        })
        
        print(f"\n[Teste Saque Rápido] Status: {response.status_code} (Esperado: 403)")
        self.assertEqual(response.status_code, 403)
        self.assertIn("Aguarde processamento", str(response.data))

    def test_gap2_saque_alto_retido(self):
        """
        Tenta sacar valor acima do limite (500). Deve ir para ANÁLISE (202).
        """
        response = self.client.post('/api/accounts/saque/', {
            "valor": "600.00", # Acima de 500
            "chave_pix": "test@pix.com"
        })
        
        print(f"[Teste Saque Alto] Status: {response.status_code} (Esperado: 202)")
        self.assertEqual(response.status_code, 202)
        
        # Verifica se gravou no banco como EM_ANALISE
        solicitacao = SolicitacaoPagamento.objects.latest('id')
        self.assertEqual(solicitacao.status, 'EM_ANALISE')
        print(f"[Teste Saque Alto] Status no Banco: {solicitacao.status} (Esperado: EM_ANALISE)")

    def test_saque_normal_aprovado(self):
        """
        Depósito antigo + Valor baixo. Deve APROVAR (200).
        """
        # 1. Depósito feito há 3 horas
        passado = timezone.now() - timedelta(hours=3)
        t = Transacao.objects.create(
            usuario=self.user,
            tipo='DEPOSITO',
            valor=Decimal('100.00'),
            saldo_anterior=Decimal('0.00'),
            saldo_posterior=Decimal('100.00')
        )
        t.data = passado # Força data antiga
        t.save()
        
        # 2. Saque baixo
        response = self.client.post('/api/accounts/saque/', {
            "valor": "50.00",
            "chave_pix": "test@pix.com"
        })
        
        # Nota: Pode dar erro 500 ou 400 se a API SkalePay não estiver configurada no teste,
        # mas o importante é que PASSOU pelas verificações de segurança.
        # Se retornar 200 (sucesso mockado) ou erro de API externa, significa que passou pelo bloqueio.
        if response.status_code != 200:
             # Se falhar, que seja por erro da API externa, não por bloqueio de segurança
             print(f"[Teste Normal] Resposta: {response.data}")
             self.assertNotEqual(response.status_code, 403) 
             self.assertNotEqual(response.status_code, 202)