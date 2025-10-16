#!/bin/sh
set -e

echo "Waiting for database to be ready..."
# Use Django's built-in check
until python manage.py check --database default; do
  echo "Database not ready, waiting..."
  sleep 1
done

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"
