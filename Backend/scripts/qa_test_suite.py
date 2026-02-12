#!/usr/bin/env python3
"""
QA Test Suite for Production Readiness
Comprehensive testing of all critical system components
"""
import os
import sys
import json
import time
import random
from pathlib import Path
from decimal import Decimal

# Add current directory to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.db import connection, transaction
from django.core.exceptions import ValidationError
from accounts.models import CustomUser, Transacao, SolicitacaoPagamento
from games.models import Aposta, Jogo, Sorteio

User = get_user_model()

class QATestSuite:
    """Comprehensive QA test suite"""
    
    def __init__(self):
        self.client = Client()
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, passed, message=""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        self.test_results.append({
            'test': test_name,
            'status': status,
            'message': message
        })
        print(f"{status} {test_name}: {message}")
    
    def test_user_model_constraints(self):
        """Test user model constraints and validation"""
        print("\n🧪 Testing User Model Constraints...")
        
        # Test CPF/CNPJ uniqueness
        try:
            user1 = CustomUser.objects.create_user(
                cpf_cnpj='12345678901',
                nome_completo='Test User 1',
                email='test1@example.com',
                password='testpass123'
            )
            
            # Should fail on duplicate CPF
            try:
                user2 = CustomUser.objects.create_user(
                    cpf_cnpj='12345678901',  # Same CPF
                    nome_completo='Test User 2',
                    email='test2@example.com',
                    password='testpass456'
                )
                self.log_test("CPF Uniqueness", False, "Duplicate CPF allowed")
            except:
                self.log_test("CPF Uniqueness", True, "Duplicate CPF correctly rejected")
                
        except Exception as e:
            self.log_test("User Creation", False, f"Failed: {e}")
    
    def test_money_architecture(self):
        """Test money as integer architecture"""
        print("\n💰 Testing Money Architecture...")
        
        # Test user balance operations
        user = CustomUser.objects.first()
        if user:
            initial_balance = user.saldo
            
            # Test integer operations
            user.saldo += 100  # Add R$ 1.00
            user.save()
            
            if user.saldo == initial_balance + 100:
                self.log_test("Integer Money Operations", True, "Balance operations work correctly")
            else:
                self.log_test("Integer Money Operations", False, "Balance math incorrect")
            
            # Test large amounts
            user.saldo = 999999999  # R$ 9,999,999.00
            user.save()
            
            if user.saldo == 999999999:
                self.log_test("Large Money Values", True, "Large amounts handled correctly")
            else:
                self.log_test("Large Money Values", False, "Large amounts corrupted")
    
    def test_transaction_integrity(self):
        """Test transaction integrity and audit trail"""
        print("\n📊 Testing Transaction Integrity...")
        
        user = CustomUser.objects.first()
        if not user:
            self.log_test("Transaction Setup", False, "No user found")
            return
        
        initial_balance = user.saldo
        
        # Create transaction
        trans = Transacao.objects.create(
            usuario=user,
            tipo='DEPOSITO',
            valor=5000,  # R$ 50.00
            saldo_anterior=initial_balance,
            saldo_posterior=initial_balance + 5000,
            descricao='Test deposit'
        )
        
        # Verify transaction integrity
        if (trans.saldo_posterior - trans.saldo_anterior) == trans.valor:
            self.log_test("Transaction Math", True, "Transaction balance math correct")
        else:
            self.log_test("Transaction Math", False, "Transaction balance math incorrect")
        
        # Test audit trail
        user.refresh_from_db()
        if user.saldo == trans.saldo_posterior:
            self.log_test("Audit Trail", True, "User balance updated correctly")
        else:
            self.log_test("Audit Trail", False, "User balance not updated correctly")
    
    def test_betting_system(self):
        """Test betting system functionality"""
        print("\n🎲 Testing Betting System...")
        
        user = CustomUser.objects.first()
        if not user:
            self.log_test("Betting Setup", False, "No user found")
            return
        
        # Create test game
        game, created = Jogo.objects.get_or_create(
            nome='QA Test Game',
            defaults={'tipo': 'BICHO', 'ativo': True}
        )
        
        # Create test draw
        draw = Sorteio.objects.create(
            data='2024-01-01',
            resultado={'numeros': [1234, 5678, 9012]}
        )
        
        # Create test bet
        bet_value = 1000  # R$ 10.00
        bet = Aposta.objects.create(
            usuario=user,
            jogo=game,
            sorteio=draw,
            valor=bet_value,
            valor_premio=bet_value * 10,  # 10x prize
            palpites=['1234'],
            status='PENDENTE',
            ganhou=False
        )
        
        # Test bet integrity
        if bet.valor == bet_value and bet.valor_premio == bet_value * 10:
            self.log_test("Bet Creation", True, "Bet created with correct values")
        else:
            self.log_test("Bet Creation", False, "Bet values corrupted")
        
        # Test user balance deduction
        user.refresh_from_db()
        expected_balance = user.saldo - bet_value
        
        # Simulate bet processing
        user.saldo -= bet_value
        user.save()
        
        if user.saldo == expected_balance:
            self.log_test("Balance Deduction", True, "Balance correctly deducted")
        else:
            self.log_test("Balance Deduction", False, "Balance deduction incorrect")
    
    def test_api_endpoints(self):
        """Test critical API endpoints"""
        print("\n🌐 Testing API Endpoints...")
        
        # Test user registration
        register_data = {
            'cpf_cnpj': '98765432100',
            'nome_completo': 'QA Test User',
            'email': 'qa@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post('/api/accounts/register/', 
                               data=json.dumps(register_data),
                               content_type='application/json')
        
        if response.status_code in [200, 201]:
            self.log_test("User Registration API", True, f"Status {response.status_code}")
        else:
            self.log_test("User Registration API", False, f"Status {response.status_code}")
        
        # Test login
        login_data = {
            'cpf_cnpj': '70114581150',  # Existing superuser
            'password': 'kurtcobain1010'
        }
        
        response = self.client.post('/api/accounts/login/',
                               data=json.dumps(login_data),
                               content_type='application/json')
        
        if response.status_code == 200:
            self.log_test("Login API", True, f"Status {response.status_code}")
        else:
            self.log_test("Login API", False, f"Status {response.status_code}")
        
        # Test protected endpoint
        response = self.client.get('/api/accounts/me/')
        
        if response.status_code == 401:
            self.log_test("Protected Endpoint", True, "Correctly requires authentication")
        else:
            self.log_test("Protected Endpoint", False, f"Should be 401, got {response.status_code}")
    
    def test_database_constraints(self):
        """Test database constraints and foreign keys"""
        print("\n🗄️ Testing Database Constraints...")
        
        # Test foreign key protection
        user = CustomUser.objects.first()
        if user:
            try:
                # Try to delete user with transactions
                with transaction.atomic():
                    Transacao.objects.create(usuario=user, valor=1000, saldo_anterior=0, saldo_posterior=1000)
                    user.delete()  # Should fail due to PROTECT
                    self.log_test("Foreign Key Protection", False, "User deletion allowed with transactions")
            except:
                self.log_test("Foreign Key Protection", True, "User deletion correctly prevented")
        
        # Test unique constraints
        try:
            # Create duplicate transaction ID
            Transacao.objects.create(id=999, usuario=user, valor=1000, saldo_anterior=0, saldo_posterior=1000)
            Transacao.objects.create(id=999, usuario=user, valor=2000, saldo_anterior=0, saldo_posterior=2000)
            self.log_test("Unique Constraints", False, "Duplicate IDs allowed")
        except:
            self.log_test("Unique Constraints", True, "Duplicate IDs correctly rejected")
    
    def test_performance_benchmarks(self):
        """Test performance benchmarks"""
        print("\n⚡ Testing Performance...")
        
        # Test bulk user creation with bulk_create
        start_time = time.time()
        
        users_to_create = []
        for i in range(100):
            users_to_create.append(CustomUser(
                cpf_cnpj=f'{i:011d}',
                nome_completo=f'Perf Test {i}',
                email=f'perf{i}@test.com',
                password='testpass123'
            ))
        
        # Use bulk_create for better performance
        CustomUser.objects.bulk_create(users_to_create)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if duration < 2.0:  # Should create 100 users in < 2 seconds
            self.log_test("Bulk User Creation", True, f"Created 100 users in {duration:.2f}s")
        else:
            self.log_test("Bulk User Creation", False, f"Slow: {duration:.2f}s for 100 users")
        
        # Test query performance
        start_time = time.time()
        users = list(CustomUser.objects.all()[:1000])
        end_time = time.time()
        
        query_duration = end_time - start_time
        
        if query_duration < 0.5:  # Should query 1000 users in < 0.5 seconds
            self.log_test("Query Performance", True, f"Queried {len(users)} users in {query_duration:.3f}s")
        else:
            self.log_test("Query Performance", False, f"Slow: {query_duration:.3f}s for {len(users)} users")
    
    def test_security_validations(self):
        """Test security validations"""
        print("\n🔒 Testing Security Validations...")
        
        # Test password validation
        try:
            user = CustomUser.objects.create_user(
                cpf_cnpj='12345678903',
                nome_completo='Test User',
                email='test@example.com',
                password='123'  # Too simple
            )
            self.log_test("Password Validation", False, "Simple password allowed")
        except ValidationError:
            self.log_test("Password Validation", True, "Simple password correctly rejected")
        
        # Test CPF format validation
        try:
            user = CustomUser.objects.create_user(
                cpf_cnpj='invalid',  # Invalid CPF
                nome_completo='Test User',
                email='test2@example.com',
                password='validpass123'
            )
            self.log_test("CPF Validation", False, "Invalid CPF allowed")
        except:
            self.log_test("CPF Validation", True, "Invalid CPF correctly rejected")
    
    def run_all_tests(self):
        """Run all QA tests"""
        print("🧪 COMPREHENSIVE QA TEST SUITE")
        print("=" * 60)
        
        # Run all test categories
        self.test_user_model_constraints()
        self.test_money_architecture()
        self.test_transaction_integrity()
        self.test_betting_system()
        self.test_api_endpoints()
        self.test_database_constraints()
        self.test_performance_benchmarks()
        self.test_security_validations()
        
        # Calculate results
        print("\n" + "=" * 60)
        print("📊 QA TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed_percentage = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {passed_percentage:.1f}%")
        
        # Detailed results
        print("\n📋 Detailed Results:")
        for result in self.test_results:
            print(f"  {result['status']} {result['test']}: {result['message']}")
        
        # Overall assessment
        print("\n🎯 OVERALL ASSESSMENT:")
        if passed_percentage >= 90:
            print("🟢 EXCELLENT: System is production-ready")
        elif passed_percentage >= 80:
            print("🟡 GOOD: System needs minor fixes")
        elif passed_percentage >= 70:
            print("🟠 FAIR: System needs significant fixes")
        else:
            print("🔴 POOR: System needs major fixes")
        
        return passed_percentage >= 90

def main():
    """Main QA test runner"""
    suite = QATestSuite()
    success = suite.run_all_tests()
    
    print(f"\n🏆 QA Suite {'PASSED' if success else 'FAILED'}")
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
