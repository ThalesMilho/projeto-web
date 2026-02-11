"""
Test to verify Decimal to Integer migration works correctly.
"""

from decimal import Decimal
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from unittest.mock import patch

from accounts.models import CustomUser, Transacao, SolicitacaoPagamento
from accounts.services.wallet import WalletService

User = get_user_model()


class TestMigrationVerification(TestCase):
    """Verify that Decimal to Integer migration works correctly."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            cpf_cnpj='12345678901',
            password='test123',
            nome_completo='Migration Test User'
        )
    
    def test_decimal_to_cents_conversion(self):
        """Test the conversion logic."""
        # Test various input formats
        test_cases = [
            (10.50, 1050),
            (Decimal('10.50'), 1050),
            ("10.50", 1050),
            ("1050", 1050),
            (1050, 1050),
            (0.01, 1),
            (Decimal('0.01'), 1),
        ]
        
        for input_val, expected_cents in test_cases:
            actual_cents = WalletService._convert_to_cents(input_val)
            self.assertEqual(actual_cents, expected_cents,
                           f"Conversion failed for {input_val}")
    
    def test_cents_to_decimal_conversion(self):
        """Test cents to Decimal conversion."""
        test_cases = [
            (1050, Decimal('10.50')),
            (100, Decimal('1.00')),
            (1, Decimal('0.01')),
            (0, Decimal('0.00')),
        ]
        
        for cents, expected_decimal in test_cases:
            actual_decimal = WalletService._cents_to_decimal(cents)
            self.assertEqual(actual_decimal, expected_decimal,
                           f"Decimal conversion failed for {cents}")
    
    def test_display_formatting(self):
        """Test display formatting."""
        test_cases = [
            (1050, "R$ 10.50"),
            (100, "R$ 1.00"),
            (1, "R$ 0.01"),
            (0, "R$ 0.00"),
        ]
        
        for cents, expected_display in test_cases:
            actual_display = WalletService._format_display(cents)
            self.assertEqual(actual_display, expected_display,
                           f"Display formatting failed for {cents}")
    
    def test_integer_wallet_operations(self):
        """Test wallet operations with integer architecture."""
        # Set initial balance: R$ 100.00 = 10000 cents
        self.user.saldo = 10000
        self.user.save()
        
        # Debit R$ 10.50 = 1050 cents
        tx1 = WalletService.debit(
            self.user.id, 
            10.50,  # Can pass float
            "Test debit"
        )
        
        # Check balance: 10000 - 1050 = 894.50 cents
        self.user.refresh_from_db()
        self.assertEqual(self.user.saldo, 89450)
        
        # Credit R$ 5.25 = 525 cents
        tx2 = WalletService.credit(
            self.user.id,
            "5.25",  # Can pass string
            "Test credit"
        )
        
        # Check final balance: 89450 + 525 = 89975 cents = R$ 899.75
        self.user.refresh_from_db()
        self.assertEqual(self.user.saldo, 89975)
        
        # Verify transactions stored as cents
        self.assertEqual(tx1.valor, 1050)  # R$ 10.50 as 1050 cents
        self.assertEqual(tx2.valor, 525)   # R$ 5.25 as 525 cents
    
    def test_insufficient_balance_handling(self):
        """Test insufficient balance with proper error messages."""
        # Set low balance: R$ 5.00 = 500 cents
        self.user.saldo = 500
        self.user.save()
        
        # Try to debit R$ 10.00 = 1000 cents
        with self.assertRaises(Exception) as context:
            WalletService.debit(
                self.user.id,
                10.00,
                "Overdraft attempt"
            )
        
        # Check error message contains formatted values
        error_msg = str(context.exception)
        self.assertIn("R$ 10.00", error_msg)
        self.assertIn("R$ 5.00", error_msg)
        self.assertIn("Saldo insuficiente", error_msg)
    
    def test_transfer_functionality(self):
        """Test transfer between users."""
        # Create two users
        user1 = User.objects.create_user(
            cpf_cnpj='12345678902',
            password='test123',
            nome_completo='Transfer User 1'
        )
        user2 = User.objects.create_user(
            cpf_cnpj='12345678903',
            password='test123',
            nome_completo='Transfer User 2'
        )
        
        # Set balances
        user1.saldo = 2000  # R$ 20.00
        user2.saldo = 500   # R$ 5.00
        user1.save()
        user2.save()
        
        # Transfer R$ 10.00 = 1000 cents
        debit_tx, credit_tx = WalletService.transfer(
            user1.id,
            user2.id,
            1000,
            "Test transfer"
        )
        
        # Verify final balances
        user1.refresh_from_db()
        user2.refresh_from_db()
        
        self.assertEqual(user1.saldo, 1000)  # R$ 10.00
        self.assertEqual(user2.saldo, 1500)  # R$ 15.00
        
        # Verify transactions
        self.assertEqual(debit_tx.valor, 1000)
        self.assertEqual(credit_tx.valor, 1000)
        self.assertEqual(debit_tx.tipo, 'APOSTA')
        self.assertEqual(credit_tx.tipo, 'DEPOSITO')


if __name__ == '__main__':
    import unittest
    unittest.main()
