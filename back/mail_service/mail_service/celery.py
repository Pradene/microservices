from __future__ import absolute_import, unicode_literals

import os

from mail_service import settings
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mail_service.settings')

# Create a Celery app instance
app = Celery('mail_service')

# Configure Celery with settings from Django
app.config_from_object({
    'broker_url': 'redis://redis:6379/0',  # Redis broker URL
    'result_backend': 'redis://redis:6379/0',  # Redis backend to store results
    'accept_content': ['json'],  # Accept only JSON data
    'task_serializer': 'json',  # Serialize tasks as JSON
    'timezone': 'UTC',  # Set timezone to UTC
    'task_queues': {
        'mail_queue': {
            'binding_key': 'mail_service.#',  # Mail service queue binding
        }
    },
})

# Automatically discover tasks from registered Django apps
app.autodiscover_tasks(['mail_service'])