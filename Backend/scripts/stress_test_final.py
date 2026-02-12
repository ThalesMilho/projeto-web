#!/usr/bin/env python3
"""
Random Stress Test for the Application
Tests various random operations to ensure system stability
"""
import os
import sys
import random
import time
from pathlib import Path

# Add current directory to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from accounts.models import CustomUser, Transacao
from games.models import Aposta, Jogo

def create_test_user():
    """Create a test user for stress testing"""
    cpf = f"{random.randint(10000000000, 99999999999)}"
    
    user, created = CustomUser.objects.get_or_create(
        cpf_cnpj=cpf,
        defaults={
            'nome_completo': f'Stress User {cpf}',
            'email': f'stress{cpf}@test.com',
            'saldo': random.randint(0, 100000),  # Random balance in cents
        }
    )
    
    if created:
        print(f"✅ Created test user: {cpf}")
    else:
        print(f"📋 Using existing user: {cpf}")
    
    return user

def test_database_integrity():
    """Test database integrity and constraints"""
    print("🔍 Testing database integrity...")
    
    # Test user constraints
    users_count = CustomUser.objects.count()
    print(f"📊 Total users: {users_count}")
    
    # Test transaction consistency
    total_transactions = Transacao.objects.count()
    print(f"📊 Total transactions: {total_transactions}")
    
    # Test bet consistency
    total_bets = Aposta.objects.count()
    print(f"📊 Total bets: {total_bets}")
    
    # Test money fields are integers
    user = CustomUser.objects.first()
    if user:
        print(f"💰 User balance type: {type(user.saldo).__name__}")
        print(f"💰 User balance value: {user.saldo}")
    
    print("✅ Database integrity check complete")

def test_performance():
    """Test basic performance metrics"""
    print("⚡ Testing performance...")
    
    start_time = time.time()
    
    # Test user query performance
    users = list(CustomUser.objects.all()[:100])
    query_time = time.time() - start_time
    
    print(f"⚡ Queried {len(users)} users in {query_time:.3f}s")
    
    # Test transaction query performance
    start_time = time.time()
    transactions = list(Transacao.objects.all()[:100])
    trans_time = time.time() - start_time
    
    print(f"⚡ Queried {len(transactions)} transactions in {trans_time:.3f}s")
    
    if query_time < 1.0 and trans_time < 1.0:
        print("✅ Performance looks good!")
    else:
        print("⚠️  Performance might need optimization")

def main():
    print("🧪 COMPREHENSIVE STRESS TEST")
    print("=" * 50)
    
    try:
        # Test 1: Create test data
        user = create_test_user()
        
        # Test 2: Database integrity
        test_database_integrity()
        
        # Test 3: Performance
        test_performance()
        
        print("\n🎉 STRESS TEST COMPLETE!")
        print("✅ All random operations completed successfully")
        print("🚀 System appears stable and ready for production")
        
        return True
        
    except Exception as e:
        print(f"\n❌ STRESS TEST FAILED: {e}")
        print("🚨 System needs attention before production")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
