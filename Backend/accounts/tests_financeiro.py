from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class FinanceiroTests(TestCase):
    def setUp(self):
        """Prepara um utilizador limpo antes de cada teste"""
        self.user = User.objects.create_user(
            cpf_cnpj="10020030044",
            password="senha_forte_123",
            nome_completo="Apostador de Teste"
        )

    def test_primeiro_deposito_gera_bonus(self):
        """Teste: Deposita 100 -> Ganha 100 de bónus -> Rollover vira 400"""
        valor_deposito = Decimal('100.00')
        
        # 1. Aplica a lógica
        bonus = self.user.aplicar_bonus_deposito(valor_deposito)
        self.user.saldo += valor_deposito + bonus
        self.user.save()

        # 2. Verificações
        self.assertEqual(bonus, Decimal('100.00'), "O bónus deve ser 100% do valor")
        self.assertEqual(self.user.saldo, Decimal('200.00'), "Saldo final deve ser 200")
        self.assertTrue(self.user.recebeu_bonus, "Flag recebeu_bonus deve ser True")
        
        # Rollover = (100 depósito + 100 bónus) * 2 = 400
        self.assertEqual(self.user.meta_rollover, Decimal('400.00'), "Meta de rollover incorreta")

    def test_teto_maximo_do_bonus(self):
        """Teste: Deposita 1000 -> Bónus limita-se a 500 (Regra do Teto)"""
        valor_deposito = Decimal('1000.00')
        
        bonus = self.user.aplicar_bonus_deposito(valor_deposito)
        
        self.assertEqual(bonus, Decimal('500.00'), "O bónus não respeitou o teto de 500")

    def test_segundo_deposito_nao_gera_bonus(self):
        """Teste: Utilizador antigo não ganha bónus de boas-vindas duas vezes"""
        # 1. Simula que já recebeu antes
        self.user.recebeu_bonus = True
        self.user.save()

        # 2. Tenta novo depósito
        bonus = self.user.aplicar_bonus_deposito(Decimal('100.00'))
        
        self.assertEqual(bonus, Decimal('0.00'), "Não deve gerar bónus no 2º depósito")

    def test_bloqueio_de_saque_por_rollover(self):
        """Teste: Tem saldo, mas não cumpriu o rollover -> Saque Bloqueado"""
        self.user.saldo = Decimal('500.00')
        self.user.meta_rollover = Decimal('400.00')
        self.user.total_apostado_rollover = Decimal('100.00') # Apostou pouco
        self.user.save()

        # Verifica se pode sacar
        pode = self.user.pode_sacar()
        falta = self.user.quanto_falta_rollover()

        self.assertFalse(pode, "O saque deveria estar bloqueado")
        self.assertEqual(falta, Decimal('300.00'), "O cálculo de quanto falta está errado")

    def test_liberacao_de_saque_sucesso(self):
        """Teste: Cumpriu a meta de apostas -> Saque Liberado"""
        self.user.saldo = Decimal('1000.00')
        self.user.meta_rollover = Decimal('400.00')
        
        # Apostou mais que a meta
        self.user.total_apostado_rollover = Decimal('401.00') 
        self.user.save()

        self.assertTrue(self.user.pode_sacar(), "O saque deveria estar liberado")
        self.assertEqual(self.user.quanto_falta_rollover(), 0, "Deveria faltar 0")