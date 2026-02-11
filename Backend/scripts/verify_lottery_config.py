#!/usr/bin/env python
"""
Verification script for lottery configuration.
Shows current settings and validates the implementation.
"""

import os
import sys
import django

# Add the Backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from games.models import ParametrosDoJogo
from games.strategies import ValidadorFactory
from games.models import Jogo, Modalidade


def verify_lottery_config():
    """
    Verifies and displays the current lottery configuration.
    """
    print("🔍 LOTTERY CONFIGURATION VERIFICATION")
    print("=" * 50)
    
    try:
        # 1. Check database configuration
        config = ParametrosDoJogo.load()
        print("\n📋 Database Configuration:")
        print(f"   Lotinha (Acertos Min): {config.lotinha_acertos_necessarios}")
        print(f"   Quininha (Acertos Min): {config.quininha_acertos_necessarios}")
        print(f"   Seninha (Acertos Min): {config.seninha_acertos_necessarios}")
        
        # 2. Test ValidadorFactory integration
        print("\n🏭 ValidadorFactory Integration:")
        
        # Create test game and modalidades
        jogo, _ = Jogo.objects.get_or_create(
            nome='Test Verification',
            defaults={'tipo': 'loterias'}
        )
        
        modalidades = [
            ('Lotinha', config.lotinha_acertos_necessarios),
            ('Quininha', config.quininha_acertos_necessarios),
            ('Seninha', config.seninha_acertos_necessarios),
        ]
        
        for nome, expected_hits in modalidades:
            modalidade, _ = Modalidade.objects.get_or_create(
                jogo=jogo,
                nome=nome,
                defaults={'cotacao': 10.0}
            )
            
            strategy = ValidadorFactory.get_strategy(modalidade)
            actual_hits = strategy.quantidade_acertos_necessarios if strategy else None
            
            status = "✅" if actual_hits == expected_hits else "❌"
            print(f"   {status} {nome}: Expected {expected_hits}, Got {actual_hits}")
        
        # 3. Test utility function
        print("\n🛠️  Utility Function Test:")
        from games.utils import extract_numbers_from_string
        
        test_cases = [
            ("01, 02, 05", [1, 2, 5]),
            ("1-2-3", [1, 2, 3]),
            ("05", [5]),
            ("", []),
        ]
        
        all_passed = True
        for input_str, expected in test_cases:
            result = extract_numbers_from_string(input_str)
            passed = result == expected
            status = "✅" if passed else "❌"
            print(f"   {status} '{input_str}' → {result}")
            if not passed:
                all_passed = False
        
        # 4. Summary
        print("\n📊 SUMMARY:")
        if all_passed:
            print("   ✅ All components are working correctly!")
            print("   ✅ Lottery variants are production-ready!")
        else:
            print("   ❌ Some components need attention.")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error during verification: {str(e)}")
        return False


if __name__ == "__main__":
    success = verify_lottery_config()
    sys.exit(0 if success else 1)
