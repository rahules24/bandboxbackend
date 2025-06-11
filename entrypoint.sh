#!/bin/sh
set -e

echo "Waiting for database to be ready..."
# Use Django's built-in check
until python manage.py check --database default; do
  echo "Database not ready, waiting..."
  sleep 1
done

echo "Starting server..."
exec "$@"
