import logging
import json
import requests

from datetime import timedelta

from django.core.cache import cache
from django.views import View
from django.db.models import Value
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
				user_data = self.get_user(request, uid)
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
				messages = Message.objects.filter(
					room_id=room.id
				).values('id', 'user_id', 'room_id', 'content', 'created_at'
				).annotate(source=Value('message'))

				invitations = Invitation.objects.filter(
					room_id=room.id
				).values('id', 'user_id', 'room_id', 'status', 'created_at'
				).annotate(source=Value('invitation'))

				queryset = list(chain(messages, invitations))
				sorted_queryset = sorted(queryset, key=lambda x: x['created_at'])
				latest_message = sorted_queryset[-1] if sorted_queryset else None

				user_ids = [uid for uid in room.user_ids if uid != user_id]
				users_data = []
				for uid in user_ids:
					user_info = self.get_user(request, uid)
					users_data.append(user_info)
				room_name = ", ".join(user['username'] for user in users_data if user.get('username'))

				if latest_message:
					rooms_data.append({
						'id': room.id,
						'name': room_name,
						'message': {
							'content': latest_message['content'] if latest_message['source'] == 'message' else f"Invitation {latest_message['status']}",
						},
					})
				else:
					rooms_data.append({
						'id': room.id,
						'name': room_name,
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


	def get_user(self, request, user_id):
		"""
		Retrieve user data from cache or the user service.
		"""
		cached_user = cache.get(f'user:{user_id}')
		if cached_user:
			return cached_user

		try:
			token =  request.COOKIES.get('access_token')
			if not token:
				raise Exception('Token is missing')

			# Make a request to the user service if the user is not cached
			headers = {'Authorization': f'Bearer {token}'}
			response = requests.get(f'http://user-service:8000/api/users/{user_id}/', headers=headers)

			if response.status_code == 200:
				data = response.json()

				# Cache the user data for future requests
				cache.set(f'user:{user_id}', data['user'], timeout=60 * 15)
				return data.get('user')
			
			else:
				logger.error(f'Error fetching user {user_id} from user service: {response.status_code}')
				return {}  # Default user data if fetch fails
		
		except Exception as e:
			logger.error(f'Error fetching user {user_id}: {e}')
			return {}
