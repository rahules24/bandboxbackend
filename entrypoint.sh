#!/bin/sh
set -e

echo "Waiting for database to be ready..."
# Use Django's built-in check instead of pg_isready
until python manage.py check --database default; do
  echo "Database not ready, waiting..."
  sleep 1
done

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Starting server..."
exec "$@"
