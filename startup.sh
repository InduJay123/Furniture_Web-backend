#!/bin/bash

# Go to the Django project folder
cd /home/site/wwwroot/backend

# Install requirements using system Python
pip install -r ../requirements.txt

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT
