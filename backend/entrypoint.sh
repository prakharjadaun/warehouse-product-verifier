#!/bin/bash
set -e

if [ "$1" = "worker" ]; then
    echo "Starting Celery worker..."
    exec celery -A app.celery_app worker --loglevel=info --concurrency=2
else
    echo "Running database migrations..."
    alembic upgrade head
    echo "Starting FastAPI server..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
