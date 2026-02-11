#!/usr/bin/env python
"""
Seeding script for lottery rules configuration.
Sets up reasonable defaults for Lotinha, Quininha, and Seninha.
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


def seed_lottery_rules():
    """
    Seeds the database with lottery configuration defaults.
    Creates or updates the ParametrosDoJogo singleton.
    """
    try:
        # Get or create the singleton instance
        config, created = ParametrosDoJogo.objects.get_or_create(
            pk=1,  # Assuming singleton with pk=1
            defaults={
                'lotinha_acertos_necessarios': 15,
                'quininha_acertos_necessarios': 5,
                'seninha_acertos_necessarios': 6,
            }
        )
        
        if not created:
            # Update existing configuration
            config.lotinha_acertos_necessarios = 15
            config.quininha_acertos_necessarios = 5
            config.seninha_acertos_necessarios = 6
            config.save()
            print("✅ Updated existing ParametrosDoJogo configuration")
        else:
            print("✅ Created new ParametrosDoJogo configuration")
        
        # Display current configuration
        print("\n📋 Current Lottery Configuration:")
        print(f"   Lotinha (Acertos Min): {config.lotinha_acertos_necessarios}")
        print(f"   Quininha (Acertos Min): {config.quininha_acertos_necessarios}")
        print(f"   Seninha (Acertos Min): {config.seninha_acertos_necessarios}")
        
        print("\n🎯 Configuration updated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating configuration: {str(e)}")
        return False


if __name__ == "__main__":
    print("🚀 Starting lottery rules seeding...")
    success = seed_lottery_rules()
    
    if success:
        print("✅ Seeding completed successfully!")
        sys.exit(0)
    else:
        print("❌ Seeding failed!")
        sys.exit(1)
