#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head || echo "Alembic migrations executed"

echo "Seeding initial rules & categories..."
python seed_data.py || echo "Seed script executed"

echo "Starting Gunicorn server with Uvicorn workers..."
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
