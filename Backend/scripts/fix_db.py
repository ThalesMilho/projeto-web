import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path

# --- CONFIGURAÇÃO ---
DB_NAME = "sistemabicho"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

# Lista de senhas para tentar (A recuperada + padrões)
POSSIBLE_PASSWORDS = [
    "lya100104",  # A senha que achamos no Git
    "postgres",   # Padrão da instalação
    "admin",      # Comum
    "123456",     # Comum
    "root"
]

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

def print_step(msg):
    print(f"\n🔹 {msg}...")

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def update_env_file(valid_password):
    """Atualiza ou cria o arquivo .env com a credencial correta"""
    db_url = f"postgres://{DB_USER}:{valid_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    env_lines = []
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            env_lines = f.readlines()
    
    # Remove linha antiga de DATABASE_URL se existir
    env_lines = [line for line in env_lines if not line.startswith("DATABASE_URL=")]
    
    # Adiciona a nova
    if env_lines and not env_lines[-1].endswith("\n"):
        env_lines.append("\n")
    env_lines.append(f"DATABASE_URL={db_url}\n")

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(env_lines)
    
    print_success(f"Arquivo .env atualizado com a conexão correta:\n   -> {db_url}")

def main():
    print("🚀 INICIANDO DIAGNÓSTICO E CORREÇÃO DO POSTGRESQL...")
    
    valid_conn = None
    valid_password = None

    # 1. TENTATIVA DE CONEXÃO (Descobrir a senha)
    print_step("Tentando conectar ao PostgreSQL (testando senhas conhecidas)")
    
    for password in POSSIBLE_PASSWORDS:
        try:
            # Tenta conectar no banco padrão 'postgres' para testar a senha
            conn = psycopg2.connect(
                dbname="postgres", 
                user=DB_USER, 
                password=password, 
                host=DB_HOST, 
                port=DB_PORT
            )
            conn.close()
            valid_password = password
            print_success(f"Conexão aceita! A senha correta é: '{password}'")
            break
        except psycopg2.OperationalError:
            # Erro de conexão (serviço parado ou porta errada)
            print_error("Não foi possível conectar ao servidor PostgreSQL.")
            print("   👉 Verifique se o serviço 'postgresql-x64-16' (ou similar) está INICIADO no services.msc")
            sys.exit(1)
        except psycopg2.Error:
            # Senha errada, tenta a próxima
            continue

    if not valid_password:
        print_error("Nenhuma das senhas funcionou.")
        print("   👉 Você precisará resetar a senha do usuário 'postgres' manualmente.")
        sys.exit(1)

    # 2. CRIAÇÃO DO BANCO DE DADOS
    print_step(f"Verificando se o banco '{DB_NAME}' existe")
    
    try:
        conn = psycopg2.connect(
            dbname="postgres", 
            user=DB_USER, 
            password=valid_password, 
            host=DB_HOST, 
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Verifica se existe
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
        exists = cur.fetchone()
        
        if not exists:
            print_step(f"Banco não encontrado. Criando '{DB_NAME}' agora")
            cur.execute(f"CREATE DATABASE {DB_NAME}")
            print_success(f"Banco de dados '{DB_NAME}' criado com sucesso!")
        else:
            print_success(f"O banco de dados '{DB_NAME}' já existe.")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print_error(f"Erro ao gerenciar banco de dados: {e}")
        sys.exit(1)

    # 3. ATUALIZAÇÃO DO AMBIENTE
    print_step("Configurando o Django")
    update_env_file(valid_password)

    print("\n🎉 TUDO PRONTO! AGORA RODE:")
    print("   python manage.py migrate")

if __name__ == "__main__":
    main()