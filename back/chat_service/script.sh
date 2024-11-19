#!bin/bash/

cd /app

python3 manage.py makemigrations chat_service
python3 manage.py migrate

daphne -b 0.0.0.0 -p 8000 chat_service.asgi:application &

celery -A chat_service.celery worker -Q chat_queue --loglevel=info &

wait