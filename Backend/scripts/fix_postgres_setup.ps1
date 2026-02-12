# PostgreSQL Setup Script for Windows
# Run this as Administrator in PowerShell

Write-Host "🔧 PostgreSQL Setup for Windows" -ForegroundColor Cyan
Write-Host "=" * 50

# Step 1: Set postgres user password
Write-Host "📝 Step 1: Setting postgres user password..." -ForegroundColor Yellow

# Try to connect to psql and set password
$psqlCommands = @"
ALTER USER postgres PASSWORD 'postgres';
\q
"@

try {
    $psqlCommands | psql -U postgres -d postgres
    Write-Host "✅ Postgres user password set successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to set password. Please run manually:" -ForegroundColor Red
    Write-Host "   1. Open Command Prompt as Administrator" -ForegroundColor White
    Write-Host "   2. Run: psql -U postgres -d postgres" -ForegroundColor White
    Write-Host "   3. Then run: ALTER USER postgres PASSWORD 'postgres';" -ForegroundColor White
    Write-Host "   4. Then run: \q" -ForegroundColor White
}

# Step 2: Create database and user
Write-Host "`n📝 Step 2: Creating database and user..." -ForegroundColor Yellow

$setupCommands = @"
-- Create database if it doesn't exist
SELECT 'CREATE DATABASE sistemabicho' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'sistemabicho')\gexec

-- Create user if it doesn't exist
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'projeto_web_user') THEN
      CREATE USER projeto_web_user WITH PASSWORD 'your_secure_password';
   END IF;
END
$$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE sistemabicho TO projeto_web_user;

-- List databases and users
\l
\du
\q
"@

try {
    $setupCommands | psql -U postgres -d postgres -h localhost
    Write-Host "✅ Database and user setup completed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to run setup. Please run manually:" -ForegroundColor Red
    Write-Host "   1. Open Command Prompt as Administrator" -ForegroundColor White
    Write-Host "   2. Run: psql -U postgres -d postgres -h localhost" -ForegroundColor White
    Write-Host "   3. Copy and paste the SQL commands from setupCommands variable" -ForegroundColor White
}

# Step 3: Test connection
Write-Host "`n📝 Step 3: Testing connection..." -ForegroundColor Yellow

try {
    $testResult = python -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='sistemabicho',
        user='projeto_web_user',
        password='your_secure_password'
    )
    print('✅ Connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
    Write-Host $testResult
} catch {
    Write-Host "❌ Python test failed. Check psycopg2 installation" -ForegroundColor Red
}

Write-Host "`n🎉 Setup complete!" -ForegroundColor Green
Write-Host "📋 Your DATABASE_URL should be:" -ForegroundColor Cyan
Write-Host "   DATABASE_URL=postgresql://projeto_web_user:your_secure_password@localhost:5432/sistemabicho" -ForegroundColor White
