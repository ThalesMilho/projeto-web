#!/usr/bin/env python3
"""
Test different PostgreSQL connection methods
"""
import psycopg2
from psycopg2 import OperationalError

def test_connection_methods():
    """Test various connection methods for Windows PostgreSQL"""
    
    connection_methods = [
        # Method 1: Default postgres user with no password
        {
            'name': 'postgres user, no password',
            'params': {
                'host': 'localhost',
                'port': 5432,
                'database': 'postgres',
                'user': 'postgres'
            }
        },
        # Method 2: postgres user with common passwords
        {
            'name': 'postgres user, password=postgres',
            'params': {
                'host': 'localhost',
                'port': 5432,
                'database': 'postgres',
                'user': 'postgres',
                'password': 'postgres'
            }
        },
        # Method 3: postgres user with password=password
        {
            'name': 'postgres user, password=password',
            'params': {
                'host': 'localhost',
                'port': 5432,
                'database': 'postgres',
                'user': 'postgres',
                'password': 'password'
            }
        },
        # Method 4: Try connecting to sistemabicho directly
        {
            'name': 'direct to sistemabicho, no password',
            'params': {
                'host': 'localhost',
                'port': 5432,
                'database': 'sistemabicho',
                'user': 'postgres'
            }
        }
    ]
    
    for method in connection_methods:
        print(f"\n🔍 Testing: {method['name']}")
        try:
            conn = psycopg2.connect(**method['params'])
            print(f"✅ SUCCESS with: {method['name']}")
            
            # Test basic query
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"📋 PostgreSQL: {version.split()[1]}")
            
            cursor.close()
            conn.close()
            return method['params']
            
        except OperationalError as e:
            print(f"❌ FAILED: {str(e)}")
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    return None

def main():
    print("🔍 PostgreSQL Connection Method Tester")
    print("=" * 50)
    
    working_params = test_connection_methods()
    
    if working_params:
        print(f"\n🎉 Found working connection method!")
        print(f"📋 Working parameters:")
        for key, value in working_params.items():
            if key == 'password':
                print(f"   {key}: {'*' * len(str(value))}")
            else:
                print(f"   {key}: {value}")
        
        print(f"\n💡 Next steps:")
        print(f"1. Create database: CREATE DATABASE sistemabicho;")
        print(f"2. Create user: CREATE USER projeto_web_user WITH PASSWORD 'your_password';")
        print(f"3. Grant privileges: GRANT ALL PRIVILEGES ON DATABASE sistemabicho TO projeto_web_user;")
        
    else:
        print(f"\n❌ No working connection method found!")
        print(f"💡 SOLUTION:")
        print(f"1. Check PostgreSQL service: Get-Service -Name *postgresql*")
        print(f"2. Try manual connection: psql -U postgres")
        print(f"3. Check PostgreSQL installation")

if __name__ == "__main__":
    main()
