import logging
import asyncio

from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from chat_service.celery import app
from chat_service.models import Room

logger = logging.getLogger(__name__)

@app.task(queue='chat_queue')
def create_chat(user_ids, is_private):
	try:
		logger.info(f'creating room for {user_ids}')

		if isinstance(user_ids, list):
			# Optionally, ensure all elements in the list are integers
			user_ids = [int(user_id) for user_id in user_ids if isinstance(user_id, int)]
		else:
			# Handle the case where user_ids is not a list
			logger.info('user ids is not a list')
			user_ids = []

		room = Room.objects.create(
			is_private=is_private,
			user_ids=user_ids
		)

		logging.info(f'room created, id: {room.id}')

		room.save()

		channel_layer = get_channel_layer()

		if channel_layer is None:
			logger.error(f'Channel layer not found, cannot add user to the group')
			return

		group_name = f'chat_{room.id}'
		for user_id in user_ids:
			logger.info(f'Adding user {user_id} to group {group_name}')
			channel_name = cache.get(f'user{user_id}_chat_wschannel')
			if channel_name:
				logger.info(f'channel_name of user {user_id} : {channel_name}')
				async_to_sync(channel_layer.group_add)(
					group_name,
					channel_name
				)

		return f'Task completed'

	except Exception as e:
		logger.error(f'Error during chat room creation: {str(e)}')
		return f'Task error'

