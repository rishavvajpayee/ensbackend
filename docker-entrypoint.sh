#!/bin/bash
set -e

echo "=========================================="
echo "ENS Network Graph Backend - Starting Up"
echo "=========================================="

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "✓ PostgreSQL is ready!"

# Run database migration
echo ""
echo "Running database migration..."
python migrate_db.py --auto-migrate

# Initialize database (creates tables if needed)
echo ""
echo "Initializing database..."
python init_db.py --auto-seed

echo ""
echo "=========================================="
echo "✓ Startup complete! Starting application..."
echo "=========================================="
echo ""

# Start the FastAPI application
exec uvicorn main:app --host 0.0.0.0 --port 8000

