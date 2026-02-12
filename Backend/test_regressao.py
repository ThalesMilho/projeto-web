#!/usr/bin/env python3
"""
Teste de Regressão Completo
Verifica se a alteração do CORS afetou outros campos
"""
import os
import sys
import json
import urllib.request
from pathlib import Path

# Add current directory to Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from accounts.models import CustomUser, Transacao
from games.models import Aposta

User = get_user_model()

class RegressaoTestSuite:
    """Teste de regressão completo"""
    
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
    
    def test_database_connection(self):
        """Testa se conexão com PostgreSQL ainda funciona"""
        print("\n🗄️ Testando Conexão com PostgreSQL...")
        
        try:
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result[0] == 1:
                self.log_test("PostgreSQL Connection", True, "Conexão OK")
            else:
                self.log_test("PostgreSQL Connection", False, "Query falhou")
            cursor.close()
        except Exception as e:
            self.log_test("PostgreSQL Connection", False, f"Erro: {e}")
    
    def test_user_model_integrity(self):
        """Testa se modelo CustomUser continua funcionando"""
        print("\n👤 Testando Modelo CustomUser...")
        
        try:
            # Testar criação de usuário
            user = CustomUser.objects.create_user(
                cpf_cnpj='99999999999',
                nome_completo='Test Regressão',
                email='regressao@test.com',
                password='testpass123'
            )
            
            # Verificar campos essenciais
            checks = [
                (user.cpf_cnpj == '99999999999', 'CPF correto'),
                (user.nome_completo == 'Test Regressão', 'Nome correto'),
                (user.email == 'regressao@test.com', 'Email correto'),
                (isinstance(user.saldo, int), 'Saldo é inteiro'),
                (user.saldo >= 0, 'Saldo não negativo')
            ]
            
            for check, desc in checks:
                if check:
                    self.log_test(f"User Model - {desc}", True, "OK")
                else:
                    self.log_test(f"User Model - {desc}", False, "Falhou")
                    
        except Exception as e:
            self.log_test("User Model Creation", False, f"Erro: {e}")
    
    def test_money_architecture(self):
        """Testa se arquitetura de dinheiro continua intacta"""
        print("\n💰 Testando Arquitetura de Dinheiro...")
        
        try:
            user = CustomUser.objects.first()
            if not user:
                self.log_test("Money Architecture", False, "Nenhum usuário encontrado")
                return
            
            # Testar operações com dinheiro
            initial_balance = user.saldo
            user.saldo += 5000  # R$ 50,00
            user.save()
            
            user.refresh_from_db()
            
            checks = [
                (isinstance(user.saldo, int), 'Saldo continua inteiro'),
                (user.saldo == initial_balance + 5000, 'Cálculo correto'),
                (user.saldo >= 0, 'Saldo não negativo')
            ]
            
            for check, desc in checks:
                if check:
                    self.log_test(f"Money Architecture - {desc}", True, "OK")
                else:
                    self.log_test(f"Money Architecture - {desc}", False, "Falhou")
                    
        except Exception as e:
            self.log_test("Money Architecture", False, f"Erro: {e}")
    
    def test_api_endpoints(self):
        """Testa se endpoints da API ainda funcionam"""
        print("\n🌐 Testando Endpoints da API...")
        
        # Testar endpoint público
        try:
            req = urllib.request.Request(
                'http://127.0.0.1:8000/api/games/bichos/',
                headers={
                    'Origin': 'http://localhost:3000',
                    'Content-Type': 'application/json'
                }
            )
            response = urllib.request.urlopen(req, timeout=5)
            
            # Verificar CORS
            cors_origin = response.headers.get('Access-Control-Allow-Origin')
            if cors_origin == 'http://localhost:3000':
                self.log_test("CORS Configuration", True, "Frontend permitido")
            else:
                self.log_test("CORS Configuration", False, f"CORS: {cors_origin}")
                
            # Verificar se retorna JSON
            content = response.read().decode()
            try:
                json.loads(content)
                self.log_test("API Response Format", True, "JSON válido")
            except:
                self.log_test("API Response Format", False, "JSON inválido")
                
        except Exception as e:
            self.log_test("API Endpoints", False, f"Erro: {e}")
    
    def test_authentication_system(self):
        """Testa se sistema de autenticação funciona"""
        print("\n🔐 Testando Sistema de Autenticação...")
        
        try:
            # Testar login
            login_data = json.dumps({
                'cpf_cnpj': '70114581150',
                'password': 'kurtcobain1010'
            })
            
            req = urllib.request.Request(
                'http://127.0.0.1:8000/api/accounts/login/',
                data=login_data.encode(),
                headers={'Content-Type': 'application/json'}
            )
            
            response = urllib.request.urlopen(req, timeout=5)
            content = response.read().decode()
            token_data = json.loads(content)
            
            # Verificar se retornou token
            if 'access' in token_data and 'refresh' in token_data:
                self.log_test("Authentication System", True, "Login funciona")
            else:
                self.log_test("Authentication System", False, "Tokens não retornados")
                
        except Exception as e:
            self.log_test("Authentication System", False, f"Erro: {e}")
    
    def test_transaction_integrity(self):
        """Testa se integridade de transações continua ok"""
        print("\n📊 Testando Integridade de Transações...")
        
        try:
            user = CustomUser.objects.first()
            if not user:
                self.log_test("Transaction Integrity", False, "Nenhum usuário")
                return
            
            # Criar transação teste
            trans = Transacao.objects.create(
                usuario=user,
                tipo='TESTE',
                valor=1000,
                saldo_anterior=user.saldo,
                saldo_posterior=user.saldo + 1000,
                descricao='Teste de regressão'
            )
            
            # Verificar integridade
            checks = [
                (trans.usuario == user, 'Usuário correto'),
                (trans.valor == 1000, 'Valor correto'),
                (trans.tipo == 'TESTE', 'Tipo correto'),
                (trans.saldo_posterior - trans.saldo_anterior == trans.valor, 'Matemática correta')
            ]
            
            for check, desc in checks:
                if check:
                    self.log_test(f"Transaction Integrity - {desc}", True, "OK")
                else:
                    self.log_test(f"Transaction Integrity - {desc}", False, "Falhou")
                    
        except Exception as e:
            self.log_test("Transaction Integrity", False, f"Erro: {e}")
    
    def test_settings_configuration(self):
        """Testa se configurações estão corretas"""
        print("\n⚙️ Testando Configurações...")
        
        try:
            from django.conf import settings
            
            checks = [
                (hasattr(settings, 'CORS_ALLOWED_ORIGINS'), 'CORS_ALLOWED_ORIGINS existe'),
                ('http://localhost:3000' in getattr(settings, 'CORS_ALLOWED_ORIGINS', []), 'Frontend permitido'),
                (hasattr(settings, 'DATABASES'), 'DATABASES configurado'),
                ('postgresql' in settings.DATABASES['default']['ENGINE'], 'PostgreSQL ativo'),
                (hasattr(settings, 'SECRET_KEY'), 'SECRET_KEY existe'),
                (len(settings.SECRET_KEY) > 10, 'SECRET_KEY válido')
            ]
            
            for check, desc in checks:
                if check:
                    self.log_test(f"Settings - {desc}", True, "OK")
                else:
                    self.log_test(f"Settings - {desc}", False, "Falhou")
                    
        except Exception as e:
            self.log_test("Settings Configuration", False, f"Erro: {e}")
    
    def run_all_tests(self):
        """Executa todos os testes de regressão"""
        print("🧪 TESTE DE REGRESSÃO COMPLETO")
        print("=" * 60)
        print("Verificando se alteração do CORS afetou outros campos...")
        
        # Executar todos os testes
        self.test_database_connection()
        self.test_user_model_integrity()
        self.test_money_architecture()
        self.test_api_endpoints()
        self.test_authentication_system()
        self.test_transaction_integrity()
        self.test_settings_configuration()
        
        # Calcular resultados
        print("\n" + "=" * 60)
        print("📊 RESULTADOS DO TESTE DE REGRESSÃO")
        print("=" * 60)
        
        passed_percentage = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"Total de Testes: {self.total_tests}")
        print(f"Testes Passados: {self.passed_tests}")
        print(f"Testes Falhados: {self.total_tests - self.passed_tests}")
        print(f"Taxa de Sucesso: {passed_percentage:.1f}%")
        
        # Detalhes
        print("\n📋 Resultados Detalhados:")
        for result in self.test_results:
            print(f"  {result['status']} {result['test']}: {result['message']}")
        
        # Avaliação final
        print("\n🎯 AVALIAÇÃO FINAL:")
        if passed_percentage >= 95:
            print("🟢 EXCELENTE: Nenhuma regressão detectada!")
            print("✅ Alteração do CORS não afetou outros campos!")
        elif passed_percentage >= 80:
            print("🟡 BOM: Pequenas regressões detectadas")
            print("⚠️  Alteração do CORS afetou alguns campos menores")
        elif passed_percentage >= 70:
            print("🟠 REGULAR: Regressões significativas")
            print("❌ Alteração do CORS afetou funcionalidades importantes")
        else:
            print("🔴 CRÍTICO: Múltiplas regressões")
            print("🚨 Alteração do CORS quebrou o sistema!")
        
        return passed_percentage >= 95

def main():
    """Função principal"""
    suite = RegressaoTestSuite()
    success = suite.run_all_tests()
    
    print(f"\n🏆 Teste de Regressão: {'APROVADO' if success else 'REPROVADO'}")
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
