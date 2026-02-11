"""
Simple test to verify integer refactor works correctly.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.services.wallet import WalletService

User = get_user_model()


class TestIntegerRefactor(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            cpf_cnpj='12345678901',
            password='test123',
            nome_completo='Test User'
        )
    
    def test_wallet_service_integer_operations(self):
        """Test that wallet service works with integer cents."""
        # Set initial balance: R$ 100.00 = 10000 cents
        self.user.saldo = 10000
        self.user.save()
        
        # Test debit with integer cents
        tx1 = WalletService.debit(self.user.id, 1050, "Test debit")  # R$ 10.50
        self.user.refresh_from_db()
        self.assertEqual(self.user.saldo, 89450)  # R$ 894.50
        
        # Test credit with float conversion
        tx2 = WalletService.credit(self.user.id, 10.50, "Test credit")  # R$ 10.50
        self.user.refresh_from_db()
        self.assertEqual(self.user.saldo, 90500)  # R$ 905.00
        
        # Verify transactions stored as cents
        self.assertEqual(tx1.valor, 1050)
        self.assertEqual(tx2.valor, 1050)
        
        print("✅ PASS: Integer wallet operations work correctly")
    
    def test_conversion_functions(self):
        """Test conversion helper functions."""
        # Test cents to decimal
        self.assertEqual(float(WalletService._cents_to_decimal(1050)), 10.50)
        
        # Test display formatting
        self.assertEqual(WalletService._format_display(1050), "R$ 10.50")
        
        # Test amount validation
        self.assertEqual(WalletService._validate_amount_cents(10.50), 1050)
        self.assertEqual(WalletService._validate_amount_cents("10.50"), 1050)
        self.assertEqual(WalletService._validate_amount_cents(1050), 1050)
        
        print("✅ PASS: Conversion functions work correctly")
    
    def test_error_handling(self):
        """Test error handling with proper messages."""
        self.user.saldo = 1000  # R$ 10.00
        self.user.save()
        
        # Test insufficient balance
        with self.assertRaises(ValueError) as context:
            WalletService.debit(self.user.id, 2000, "Overdraft")  # R$ 20.00
        
        self.assertIn("Saldo insuficiente", str(context.exception))
        self.assertIn("R$ 20.00", str(context.exception))
        self.assertIn("R$ 10.00", str(context.exception))
        
        print("✅ PASS: Error handling works correctly")


if __name__ == '__main__':
    import unittest
    unittest.main()
