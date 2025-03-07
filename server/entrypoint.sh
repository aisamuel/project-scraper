#!/bin/sh

echo "Waiting for PostgreSQL database to be ready..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 0.1
done
echo "Database is ready!"

# Apply migrations
echo "Make database migrations..."
python manage.py makemigrations --noinput

# Apply migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Daphne server
echo "Starting Gunicorn server..."
exec gunicorn -b 0.0.0.0:8000 product_scraper.wsgi:application
