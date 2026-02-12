#!/bin/bash
set -e

# Function to wait for database
wait_for_db() {
    echo "Waiting for PostgreSQL to be ready..."
    while ! nc -z db 5432; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 1
    done
    echo "PostgreSQL is up - continuing..."
}

# Wait for database
wait_for_db

# Run Django migrations
echo "Running Django migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Execute the command passed to the container
echo "Starting application..."
exec "$@"
