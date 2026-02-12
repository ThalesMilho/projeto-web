#!/usr/bin/env python3
"""
PostgreSQL Connection Diagnostic Tool
 isolates database connectivity issues from Django
"""
import os
import sys
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv

def load_env_vars():
    """Load environment variables from .env file"""
    # Try to find .env file in different locations
    env_paths = [
        '.env',
        '../.env',
        '../../.env',
    ]
    
    for env_path in env_paths:
        if os.path.exists(env_path):
            print(f"✅ Found .env at: {os.path.abspath(env_path)}")
            load_dotenv(env_path)
            break
    else:
        print("❌ No .env file found!")
        return False
    
    return True

def parse_database_url():
    """Parse DATABASE_URL from environment"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables!")
        print("📝 Current environment variables:")
        for key, value in os.environ.items():
            if 'DATABASE' in key or 'DB' in key:
                print(f"   {key}: {value}")
        return None
    
    print(f"🔗 DATABASE_URL found: {database_url}")
    return database_url

def test_psycopg2_connection(database_url):
    """Test direct psycopg2 connection"""
    print("\n🔍 Testing PostgreSQL connection with psycopg2...")
    
    try:
        # Parse connection parameters
        conn_params = psycopg2.extensions.parse_dsn(database_url)
        print(f"📊 Connection parameters:")
        print(f"   Host: {conn_params.get('host', 'localhost')}")
        print(f"   Port: {conn_params.get('port', 5432)}")
        print(f"   Database: {conn_params.get('dbname', 'N/A')}")
        print(f"   User: {conn_params.get('user', 'N/A')}")
        
        # Attempt connection
        print("\n🚀 Attempting connection...")
        conn = psycopg2.connect(
            host=conn_params.get('host', 'localhost'),
            port=conn_params.get('port', 5432),
            database=conn_params.get('dbname'),
            user=conn_params.get('user'),
            password=conn_params.get('password'),
            connect_timeout=10  # 10 second timeout
        )
        
        print("✅ CONNECTION SUCCESSFUL!")
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"📋 PostgreSQL Version: {version}")
        
        # Test database existence
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]
        print(f"🗄️  Current Database: {db_name}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except OperationalError as e:
        error_msg = str(e)
        print(f"❌ CONNECTION FAILED: {error_msg}")
        
        # Analyze specific error patterns
        if "connection refused" in error_msg.lower():
            print("\n🔧 DIAGNOSIS: PostgreSQL service is not running")
            print("💡 SOLUTION:")
            print("   1. Check if PostgreSQL service is running:")
            print("      Get-Service -Name *postgresql*")
            print("   2. Start PostgreSQL service:")
            print("      Start-Service -Name 'postgresql-x64-16' -Force")
            print("   3. Or start all PostgreSQL services:")
            print("      Get-Service -Name *postgresql* | Start-Service")
            
        elif "authentication failed" in error_msg.lower():
            print("\n🔧 DIAGNOSIS: Authentication failed")
            print("💡 SOLUTION:")
            print("   1. Check username/password in DATABASE_URL")
            print("   2. Verify user exists in PostgreSQL:")
            print("      psql -U postgres -c \"\\du\"")
            print("   3. Create user if needed:")
            print("      CREATE USER projeto_web_user WITH PASSWORD 'your_password';")
            
        elif "database" in error_msg.lower() and "does not exist" in error_msg.lower():
            print("\n🔧 DIAGNOSIS: Database does not exist")
            print("💡 SOLUTION:")
            print("   1. Create database:")
            print("      CREATE DATABASE sistemabicho;")
            print("   2. Grant permissions:")
            print("      GRANT ALL PRIVILEGES ON DATABASE sistemabicho TO projeto_web_user;")
            
        elif "timeout" in error_msg.lower():
            print("\n🔧 DIAGNOSIS: Connection timeout")
            print("💡 SOLUTION:")
            print("   1. Check if PostgreSQL is running on correct port")
            print("   2. Verify firewall settings")
            print("   3. Check network connectivity")
            
        elif "scram-sha-256" in error_msg.lower():
            print("\n🔧 DIAGNOSIS: Authentication method mismatch")
            print("💡 SOLUTION:")
            print("   1. Update PostgreSQL pg_hba.conf for password authentication")
            print("   2. Or update user password with proper encryption")
            
        else:
            print("\n🔧 DIAGNOSIS: Unknown connection error")
            print("💡 SOLUTION:")
            print("   1. Check PostgreSQL service status")
            print("   2. Verify connection parameters")
            print("   3. Check network connectivity")
        
        return False
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {str(e)}")
        return False

def main():
    """Main diagnostic function"""
    print("🔍 PostgreSQL Connection Diagnostic Tool")
    print("=" * 50)
    
    # Step 1: Load environment variables
    if not load_env_vars():
        sys.exit(1)
    
    # Step 2: Parse DATABASE_URL
    database_url = parse_database_url()
    if not database_url:
        print("\n💡 TO FIX:")
        print("   Add DATABASE_URL to your .env file:")
        print("   DATABASE_URL=postgresql://username:password@localhost:5432/sistemabicho")
        sys.exit(1)
    
    # Step 3: Test connection
    success = test_psycopg2_connection(database_url)
    
    if success:
        print("\n🎉 DIAGNOSIS COMPLETE: Connection successful!")
        print("✅ Your PostgreSQL setup is working correctly")
        print("🚀 Ready to run Django migrations")
    else:
        print("\n⚠️  DIAGNOSIS COMPLETE: Connection failed!")
        print("🔧 Follow the solution steps above to fix the issue")

if __name__ == "__main__":
    main()
