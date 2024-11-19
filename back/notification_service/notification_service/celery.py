from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_service.settings')

# Create a Celery app instance
app = Celery('notification_service')

# Configure Celery with settings from Django
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(
    CELERY_BROKER_URL = 'redis://redis:6379/0',
    CELERY_ACCEPT_CONTENT = ['json'],
    CELERY_TASK_SERIALIZER = 'json',
    CELERY_RESULT_BACKEND = 'redis://redis:6379/0',
    CELERY_TIMEZONE = 'UTC'
)

app.conf.task_queues = {
    'notification_queue': {
        'binding_key': 'notification_service.#',
    }
}

# Automatically discover tasks from registered Django apps
app.autodiscover_tasks(['notification_service'])