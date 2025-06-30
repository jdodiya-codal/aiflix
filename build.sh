#!/usr/bin/env bash

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Collect static files (admin CSS, JS, etc.)
python manage.py collectstatic --noinput

# Create superuser if it doesn't already exist
echo "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='jd').exists():
    User.objects.create_superuser('jd', 'jd@example.com', '123')
" | python manage.py shell
