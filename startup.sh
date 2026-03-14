#!/bin/bash

# Activate virtual environment
source /home/site/wwwroot/venv/bin/activate

# Install requirements
pip install -r requirements.txt
python backend/manage.py migrate
python backend/manage.py collectstatic --noinput
gunicorn backend.backend.wsgi --bind 0.0.0.0:$PORT