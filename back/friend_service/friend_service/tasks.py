import logging

from friend_service import settings
from friend_service.celery import app

logger = logging.getLogger(__name__)

@app.task(queue='chat_queue')
def hello():
    logger.info(f'say hello')
    return