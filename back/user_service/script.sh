#!/bin/bash/

cd /app

python3 manage.py makemigrations user_service
python3 manage.py migrate

daphne -b 0.0.0.0 -p 8000 user_service.asgi:application &

celery -A user_service.celery worker -Q user_queue --loglevel=info &

wait