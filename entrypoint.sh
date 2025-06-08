#!/bin/sh

# Run migrations automatically
echo "Running migrations..."
python manage.py migrate

# Start Django server (adjust if you use gunicorn or other)
echo "Starting server..."
exec "$@"
