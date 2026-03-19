#!/bin/sh
set -e

echo "Running migrations..."
poetry run python manage.py migrate --noinput

echo "Collecting static files..."
poetry run python manage.py collectstatic --noinput

# Create a default superuser if DJANGO_SUPERUSER_PASSWORD is set and the user doesn't exist yet
if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    poetry run python manage.py createsuperuser \
        --noinput \
        --username "${DJANGO_SUPERUSER_USERNAME:-admin}" \
        --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" 2>/dev/null || true
fi

echo "Starting server..."
exec poetry run gunicorn --bind :8000 --workers 2 src.prisonbookproject.wsgi:application
