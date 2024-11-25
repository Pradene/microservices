#!/bin/bash/

cd /app

python3 manage.py makemigrations game_service
python3 manage.py migrate

daphne -b 0.0.0.0 -p 8000 game_service.asgi:application &

# celery -A game_service.celery worker -Q game_queue --loglevel=info &

wait