import logging
import json
import requests

from datetime import timedelta

from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator

from itertools import chain
from operator import itemgetter

from celery.result import AsyncResult

from chat_service.celery import app
from chat_service.models import Message, Room, Invitation
from chat_service.decorators import jwt_required
from chat_service.utils import create_jwt

logger = logging.getLogger(__name__)

@method_decorator(jwt_required, name='dispatch')
class RoomView(View):
	def get(self, request, room_id=None):
		user_id = request.user_id
		if room_id:
			try:
				room = Room.objects.get(id=room_id)
			except Room.DoesNotExist:
				return JsonResponse({'error': 'Room not exists'}, status=400)

			logger.info(f'getting the room {room.id}')

			messages = Message.objects.filter(room_id=room_id).order_by('created_at')
			messages_data = [{
				'id': message.id,
				'type': 'message',
				'room_id': message.room_id,
				'user_id': message.user_id,
				'content': message.content,
				'created_at': message.created_at,
			} for message in messages]

			invitations = Invitation.objects.filter(room_id=room_id).order_by('created_at')
			invitations_data = [{
				'id': invitation.id,
				'type': 'invitation',
				'room_id': invitation.room_id,
				'user_id': invitation.user_id,
				'status': invitation.status,
				'created_at': invitation.created_at,
			} for invitation in invitations]

			combined_data = (list(chain(messages_data, invitations_data)))
			sorted_messages_data = sorted(combined_data, key=itemgetter('created_at'))

			users_data = []
			for uid in room.user_ids:
				user_data = self.get_user_by_id(user_id, uid)
				if user_data:
					users_data.append({
						'id': user_data.get('id'),
						'username': user_data.get('username'),
						'picture': user_data.get('picture')
					})

			room_data = {
				'id': room.id,
				'users': users_data,
				'messages': sorted_messages_data,
			}

			return JsonResponse({'room': room_data}, status=200)
		
		else:
			rooms = Room.objects.filter(user_ids__contains=[user_id])
			rooms_data = []
			for room in rooms:
				rooms_data.append({
					'id': room.id,
				})

			return JsonResponse({'rooms': rooms_data}, status=200)


	def post(self, request, room_id=None):
		if room_id:
			return self.put(request, room_id)
		
		else:			
			data = json.loads(request.body)

			is_private = data.get('is_private', False)
			user_ids = data.get('user_ids')

			if isinstance(user_ids, list):
				# Optionally, ensure all elements in the list are integers
				user_ids = [int(user_id) for user_id in user_ids if isinstance(user_id, int)]
			else:
				logger.info('user ids is not a list')
				# Handle the case where user_ids is not a list
				user_ids = []

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

		if isinstance(user_ids, list):
			# Optionally, ensure all elements in the list are integers
			user_ids = [int(user_id) for user_id in user_ids if isinstance(user_id, int)]
		else:
			logger.info('user ids is not a list')
			# Handle the case where user_ids is not a list
			user_ids = []

		room.user_ids = user_ids
		room.save()

		return JsonResponse({'message': 'Room updated'}, status=200)

	def get_user_by_id(self, user_id, friend_id):
		try:
			url = f'http://user-service:8000/api/users/{friend_id}/'
			token = create_jwt(user_id, timedelta(minutes=2))
			headers = {
				'Authorization': f'Bearer {token}'
			}

			response = requests.get(url, headers=headers)
			if response.status_code == 200:
				data = response.json()
				user = data.get('user')
				return user

			else:
				return None

		except Exception as e:
			logger.error(f'error: {str(e)}')
			return None
