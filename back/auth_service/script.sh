#!/bin/bash/

cd /app

python3 manage.py makemigrations auth_service
python3 manage.py migrate

daphne -b 0.0.0.0 -p 8000 auth_service.asgi:application &

# celery -A auth_service.celery worker -Q auth_queue --loglevel=info

wait