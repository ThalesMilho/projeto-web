# PostgreSQL Production Setup

## 1. Install PostgreSQL
```bash
# Windows: Download from https://www.postgresql.org/download/windows/
# Or use Chocolatey: choco install postgresql
```

## 2. Create Database and User
```sql
-- Connect to PostgreSQL as superuser (postgres)
CREATE DATABASE projeto_web_db;
CREATE USER projeto_web_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE projeto_web_db TO projeto_web_user;
ALTER USER projeto_web_user CREATEDB;
```

## 3. Update .env File
```bash
DATABASE_URL=postgresql://projeto_web_user:your_secure_password@localhost:5432/projeto_web_db
```

## 4. Install psycopg2
```bash
pip install psycopg2-binary
```

## 5. Migrate to PostgreSQL
```bash
python manage.py migrate
```

## 6. Create Superuser
```bash
python manage.py createsuperuser
```

## Production Benefits
✅ Multi-user concurrency
✅ Real authentication and permissions
✅ Better performance under load
✅ Advanced features (JSON, indexes)
✅ Backup and replication support
✅ Production-ready and scalable
