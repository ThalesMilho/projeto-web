#!/usr/bin/env python3
"""
Verificação do banco de dados PostgreSQL
"""
import os
import sys
from pathlib import Path

# Add current directory to Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.db import connection

def main():
    print('🔍 VERIFICAÇÃO DO BANCO DE DADOS')
    print('=' * 50)
    
    # Verificar configuração
    db_settings = connection.settings_dict
    print(f'📊 Engine: {db_settings["ENGINE"]}')
    print(f'🗄️  Database: {db_settings["NAME"]}')
    print(f'🌐 Host: {db_settings["HOST"]}')
    print(f'🔌 Port: {db_settings["PORT"]}')
    print(f'👤 User: {db_settings["USER"]}')
    
    # Testar conexão
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()[0]
        print(f'🐘 PostgreSQL: {version.split()[1]}')
        
        # Verificar se é PostgreSQL mesmo
        if 'postgresql' in db_settings['ENGINE'].lower():
            print('\n✅ ESTÁ USANDO POSTGRESQL!')
            print('✅ CONEXÃO FUNCIONANDO!')
            print('✅ BANCO DE DADOS CONFIGURADO!')
        else:
            print('\n❌ NÃO ESTÁ USANDO POSTGRESQL!')
            
        cursor.close()
        
    except Exception as e:
        print(f'\n❌ ERRO DE CONEXÃO: {e}')

if __name__ == "__main__":
    main()
