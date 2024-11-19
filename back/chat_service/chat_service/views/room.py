import logging
import json

from django.views import View
from django.http import JsonResponse

from chat_service.celery import app
from celery.result import AsyncResult
from chat_service.models.message import Message
from chat_service.models.room import Room

logger = logging.getLogger(__name__)

class RoomView(View):
	def get(self, request, room_id=None):
		if room_id:
			try:
				room = Room.objects.get()
			except Room.DoesNotExist:
				return JsonResponse({'error': 'Room not exists'}, status=400)

			logger.info(f'getting the room {room.id}')

			return JsonResponse({}, status=200)
		
		else:
			rooms = Room.objects.all()
			return JsonResponse({'rooms': rooms}, status=200)


	def post(self, request, room_id=None):
		if room_id:
			return self.put(request, room_id)
		
		else:			
			data = json.loads(request.body)

			is_private = data.get('is_private', False)
			user_ids = data.get('user_ids')

			room = Room.objects.create(
				user_ids=user_ids,
				is_private=is_private
			)

			return JsonResponse({'message': 'room created'}, status=200)


	def put(self, request, room_id=None):
		try:
			room = Room.objects.get(id=room_id)
		except Room.DoesNotExist:
			return JsonResponse({'error': 'Room not exists, cannot update it'}, status=400)

		data = json.loads(request.body)
		user_ids = data.get('user_ids')

		room.user_ids = user_ids
		room.save()

		return JsonResponse({'message': 'Room updated'}, status=200)
