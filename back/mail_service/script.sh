#!bin/bash/

cd /app

celery -A mail_service.celery worker -Q mail_queue --loglevel=info &

wait