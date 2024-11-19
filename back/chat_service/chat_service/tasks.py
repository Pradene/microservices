import logging
import asyncio

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from chat_service.celery import app
from chat_service.models import Room

logger = logging.getLogger(__name__)

@app.task(queue='chat_queue')
def create_chat(user_ids, is_private):
	try:
		logger.info(f'creating room')
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
			async_to_sync(channel_layer.group_add)(
				group_name,
				f'chat_user_{user_id}'
			)

		message = f'Room {room.id} have been created'
		async_to_sync(channel_layer.group_send)(
			group_name,
			{
				'type': 'room_created',
				'message': message
			}
		)


		return f'Task completed'

	except Exception as e:
		logger.error(f'Error during chat room creation: {str(e)}')
		return f'Task error'

