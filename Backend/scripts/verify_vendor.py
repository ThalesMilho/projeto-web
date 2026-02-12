#!/usr/bin/env python3
"""
PostgreSQL Vendor Verification Script
Verifies that Django is running on PostgreSQL only
"""
import os
import sys
import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

def main():
    """Verify PostgreSQL vendor connection"""
    print("🔍 PostgreSQL Vendor Verification")
    print("=" * 40)
    
    try:
        # Add current directory to Python path
        import sys
        from pathlib import Path
        backend_path = Path(__file__).parent.parent
        sys.path.insert(0, str(backend_path))
        
        # Initialize Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()
        
        # Import connection after Django setup
        from django.db import connection
        
        # Get database vendor
        vendor = connection.vendor
        engine = connection.settings_dict.get('ENGINE', 'Unknown')
        
        print(f"📊 Database Vendor: {vendor}")
        print(f"🔧 Database Engine: {engine}")
        
        # CRITICAL: Verify PostgreSQL only
        if vendor == 'postgresql':
            print("✅ SUCCESS: Running on PostgreSQL")
            
            # Additional PostgreSQL-specific checks
            conn_params = connection.settings_dict
            host = conn_params.get('HOST', 'localhost')
            port = conn_params.get('PORT', 5432)
            name = conn_params.get('NAME', 'Unknown')
            
            print(f"📋 Connection Details:")
            print(f"   Host: {host}")
            print(f"   Port: {port}")
            print(f"   Database: {name}")
            
            # Test basic query
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                print(f"🐘 PostgreSQL Version: {version.split()[1]}")
                cursor.close()
                print("✅ PostgreSQL connection fully functional")
                
                return True
                
            except Exception as e:
                print(f"❌ PostgreSQL query failed: {e}")
                return False
                
        elif vendor == 'sqlite':
            print("❌ FAILURE: Running on SQLite (SECURITY RISK)")
            print("🚨 CRITICAL: SQLite fallback detected!")
            print("🔧 This application requires PostgreSQL only")
            print("💡 SOLUTION:")
            print("   1. Set DATABASE_URL environment variable")
            print("   2. Ensure PostgreSQL is running")
            print("   3. Restart application")
            return False
            
        else:
            print(f"❌ FAILURE: Unknown database vendor: {vendor}")
            print("🚨 CRITICAL: Unsupported database system")
            return False
            
    except ImproperlyConfigured as e:
        print(f"❌ CONFIGURATION ERROR: {e}")
        print("🚨 CRITICAL: Django configuration failed")
        print("💡 SOLUTION:")
        print("   1. Check DATABASE_URL environment variable")
        print("   2. Verify PostgreSQL is accessible")
        print("   3. Check .env file configuration")
        return False
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        print("🚨 CRITICAL: Verification failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
