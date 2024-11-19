#!bin/bash/

cd /app

python3 manage.py makemigrations friend_service
python3 manage.py migrate

daphne -b 0.0.0.0 -p 8000 friend_service.asgi:application &

# celery -A friend_service.celery worker -Q chat_queue --loglevel=info &

wait