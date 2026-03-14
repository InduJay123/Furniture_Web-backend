#!/bin/bash

# Activate virtual environment if you have one
# source venv/bin/activate   <-- uncomment if you have a venv

python backend/manage.py migrate
python backend/manage.py collectstatic --noinput
gunicorn backend.backend.wsgi --bind 0.0.0.0:$PORT