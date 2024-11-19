import logging
import json

from django.views import View
from django.http import JsonResponse

from chat_service.celery import app
from celery.result import AsyncResult
from chat_service.models.message import Message

from chat_service.utils import get_user

logger = logging.getLogger(__name__)

class MessageView(View):
    def get(self, request, *args, **kwargs):
        logger.info('getting a message')
        return JsonResponse({}, status=200)

    def post(self, request, *args, **kwargs):
        
        logger.info('sending a message')
        
        body = request.body
        data = json.loads(body)

        user_id = data.get('user_id')
        room_id = data.get('room_id')
        content = data.get('content')

        user = get_user(user_id)

        if user is None:
            return JsonResponse({'error': 'user not found'}, status=400)

        logger.info(f'user: {user_data.username}')

        return JsonResponse({'message': 'message sent'}, status=200)