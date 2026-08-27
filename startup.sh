#!/bin/sh
set -e

python manage.py migrate --no-input
python manage.py collectstatic --no-input

# Create superuser if it does not already exist.
# The custom User model has a required unique `phone` field, so
# `createsuperuser --noinput` is not sufficient — use an inline snippet.
python manage.py shell -c "
from django.contrib.auth import get_user_model
import os
U = get_user_model()
username = os.environ['DJANGO_SUPERUSER_USERNAME']
if not U.objects.filter(username=username).exists():
    U.objects.create_superuser(
        username=username,
        email=os.environ.get('DJANGO_SUPERUSER_EMAIL', ''),
        password=os.environ['DJANGO_SUPERUSER_PASSWORD'],
        phone=os.environ['DJANGO_SUPERUSER_PHONE'],
    )
    print('superuser created:', username)
else:
    print('superuser already exists:', username)
"

# Load hotels from the default CSV using the existing management command.
python manage.py load_hotels restaurants.csv

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
