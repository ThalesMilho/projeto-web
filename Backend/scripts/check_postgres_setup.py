#!/usr/bin/env python3
"""
Check PostgreSQL setup and create database/user if needed
"""
import psycopg2
import subprocess
import sys

def connect_to_postgres():
    """Connect to default postgres database"""
    try:
        return psycopg2.connect(
            host='localhost',
            port=5432,
            database='postgres',
            user='postgres',
            password='postgres'  # Default Windows PostgreSQL password
        )
    except:
        try:
            # Try with no password
            return psycopg2.connect(
                host='localhost',
                port=5432,
                database='postgres',
                user='postgres'
            )
        except Exception as e:
            print(f"❌ Cannot connect to PostgreSQL as postgres: {e}")
            return None

def check_database_exists(conn, db_name):
    """Check if database exists"""
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    exists = cursor.fetchone() is not None
    cursor.close()
    return exists

def check_user_exists(conn, username):
    """Check if user exists"""
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (username,))
    exists = cursor.fetchone() is not None
    cursor.close()
    return exists

def create_database(conn, db_name):
    """Create database"""
    cursor = conn.cursor()
    try:
        cursor.execute(f'CREATE DATABASE "{db_name}";')
        conn.commit()
        print(f"✅ Database '{db_name}' created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False
    finally:
        cursor.close()

def create_user(conn, username, password):
    """Create user"""
    cursor = conn.cursor()
    try:
        cursor.execute(f'CREATE USER "{username}" WITH PASSWORD %s;', (password,))
        conn.commit()
        print(f"✅ User '{username}' created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create user: {e}")
        return False
    finally:
        cursor.close()

def grant_privileges(conn, db_name, username):
    """Grant privileges to user"""
    cursor = conn.cursor()
    try:
        cursor.execute(f'GRANT ALL PRIVILEGES ON DATABASE "{db_name}" TO "{username}";')
        conn.commit()
        print(f"✅ Privileges granted to '{username}' on '{db_name}'")
        return True
    except Exception as e:
        print(f"❌ Failed to grant privileges: {e}")
        return False
    finally:
        cursor.close()

def main():
    print("🔍 PostgreSQL Setup Checker")
    print("=" * 40)
    
    # Connect to PostgreSQL
    conn = connect_to_postgres()
    if not conn:
        print("\n💡 SOLUTION:")
        print("1. Make sure PostgreSQL is installed")
        print("2. Check if postgres user has password")
        print("3. Try connecting with psql to verify:")
        print("   psql -U postgres -d postgres")
        return
    
    print("✅ Connected to PostgreSQL successfully")
    
    db_name = "sistemabicho"
    username = "projeto_web_user"
    password = "your_secure_password"
    
    # Check if database exists
    if check_database_exists(conn, db_name):
        print(f"✅ Database '{db_name}' exists")
    else:
        print(f"❌ Database '{db_name}' does not exist")
        if create_database(conn, db_name):
            print(f"✅ Database '{db_name}' created")
    
    # Check if user exists
    if check_user_exists(conn, username):
        print(f"✅ User '{username}' exists")
    else:
        print(f"❌ User '{username}' does not exist")
        if create_user(conn, username, password):
            print(f"✅ User '{username}' created")
    
    # Grant privileges
    if grant_privileges(conn, db_name, username):
        print(f"✅ Privileges granted")
    
    conn.close()
    
    print(f"\n🎉 Setup complete!")
    print(f"📋 Connection string:")
    print(f"   postgresql://{username}:{password}@localhost:5432/{db_name}")

if __name__ == "__main__":
    main()
