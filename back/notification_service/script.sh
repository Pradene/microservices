#!bin/bash/

cd /app

celery -A notification_service.celery worker --loglevel=info