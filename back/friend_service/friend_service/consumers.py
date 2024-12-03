import json
import logging
import httpx

from datetime import timedelta

from celery import Celery
from .celery import app

from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .utils import create_jwt
from .models import Friendship

logger = logging.getLogger(__name__)

class FriendsConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.user_id = self.scope.get("user_id")
		logger.info(f'User {self.user_id} try to connect to friend consumer')

		if self.user_id is not None:
			self.user = await self.get_user(self.user_id)
			if not self.user:
				await self.close()

			logger.info(f'user: {self.user}')

			await self.channel_layer.group_add(
				f"user_{self.user_id}",
				self.channel_name
			)

			await self.accept()
			logger.info(f'Connection accepted')

		else:
			await self.close()


	async def disconnect(self, close_code):
		logger.info(f'Disconnect with code: {close_code}')
		if self.user_id:
			await self.channel_layer.group_discard(
				f'user_{self.user_id}',
				self.channel_name
			)


	async def receive(self, text_data):
		data = json.loads(text_data)

		logger.info(f'data received: {data}')
		
		friend_id = int(data.get('user_id'))
		message_type = data.get('type')
		logger.info(f'consumer received a message of type: {message_type}')

		if not message_type or not friend_id:
			return

		if not self.user_id:
			return

		friend = None
		try:
			friend = await self.get_user(friend_id)
		except Exception as e:
			return await self.send(text_data=json.dumps({
				'error': f'Error will fetching friend: {str(e)}'
			}))
		
		if not friend:
			return await self.send(text_data=json.dumps({
				'error': f'Friend not found:'
			}))

		logging.info(f'friend: {friend}')

		if message_type == 'friend_request_sended':
			await self.send_friend_request(friend_id)
		
		elif message_type == "friend_request_cancelled":
			await self.cancel_friend_request(friend_id)

		elif message_type == 'friend_request_accepted':
			await self.accept_friend_request(friend_id)

		elif message_type == 'friend_request_declined':
			await self.decline_friend_request(friend_id)

		elif message_type == 'friend_removed':
			await self.remove_friend(friend_id)


	async def send_friend_request(self, friend_id):
		try:
			if self.user_id == friend_id:
				return # Exit if the request is sent to yourself

			# Check if a friend request already exists before creating it
			friendship_exist = await database_sync_to_async(
				Friendship.objects.filter((
					Q(user_id=self.user_id, friend_id=friend_id) |
					Q(user_id=friend_id, friend_id=self.user_id)
				)).exists
			)()

			if friendship_exist:
				return  # Exit if the friendship already exists

			friendship = await database_sync_to_async(
				Friendship.objects.create
			)(user_id=self.user_id, friend_id=friend_id)

			await self.channel_layer.group_send(
				f'user_{friend_id}',
				{
					'type': 'friend_response',
					'action': 'friend_request_received',
					'user': self.user
				}
			)

		except Exception as e:
			logging.info(f'error: {e}')


	async def cancel_friend_request(self, friend_id):
		try:
			friendship = await database_sync_to_async(
				Friendship.objects.get
			)(user_id=self.user_id, friend_id=friend_id, status='pending')
		except Friendship.DoesNotExist:
			logger.error('Error: request your try to cancel is not found')
			return

		await database_sync_to_async(friendship.delete)()
		
		user_data = await self.get_user(self.user_id)
		friend_data = await self.get_user(friend_id)

		logging.info(f'friend: {friend_data}')
		logging.info(f'user: {user_data}')

		await self.channel_layer.group_send(
			f'user_{friend_id}',
			{
				'type': 'friend_response',
				'action': 'friend_request_cancelled',
				'user': user_data
			}
		)

		await self.channel_layer.group_send(
			f'user_{self.user_id}',
			{
				'type': 'friend_response',
				'action': 'friend_request_cancelled',
				'user': friend_data
			}
		)



	async def accept_friend_request(self, friend_id):
		try:
			# Friend id is the id of the user who sent the request
			friendship = await database_sync_to_async(
				Friendship.objects.get
			)(user_id=friend_id, friend_id=self.user_id)
			friendship.status = 'accepted'
			await database_sync_to_async(friendship.save)()
		
		except Friendship.DoesNotExist:
			logger.error(f'Error: user you trying to accept the request is not found')
			return
		
		except Exception as e:
			logger.error(f'Error saving the status of friendship: {str(e)}')
			return

		user_data = await self.get_user(self.user_id)
		friend_data = await self.get_user(friend_id)

		logging.info(f'friend: {friend_data}')
		logging.info(f'user: {user_data}')

		await self.channel_layer.group_send(
			f'user_{self.user_id}',
			{
				'type': 'friend_response',
				'action': 'friend_request_accepted',
				'user': friend_data,
			}
		)
		
		await self.channel_layer.group_send(
			f'user_{friend_id}',
			{
				'type': 'friend_response',
				'action': 'friend_request_accepted',
				'user': user_data,
			}
		)

		try:
			app.send_task(
				'chat_service.tasks.create_chat',
				args=[[self.user_id, friend_id], True],
				queue='chat_queue'
			)

			logger.info(f'Chat creation task sent')
	
		except Exception as e:
			logger.error(f'Error during the chat creation: {str(e)}')
			return
	

	async def decline_friend_request(self, friend_id):
		try:
			friendship = await database_sync_to_async(
				Friendship.objects.get
			)(user_id=friend_id, friend_id=self.user_id)
		except Friendship.DoesNotExist:
			logger.error(f'Friend request not found, cannot decline it')
			return

		# Delete the friend request
		await database_sync_to_async(friendship.delete)()
		
		user_data = await self.get_user(self.user_id)
		friend_data = await self.get_user(friend_id)

		await self.channel_layer.group_send(
			f'user_{friend_id}',
			{
				'type': 'friend_response',
				'action': 'friend_request_declined',
				'user': user_data
			}
		)

		await self.channel_layer.group_send(
			f'user_{self.user_id}',
			{
				'type': 'friend_response',
				'action': 'friend_request_declined',
				'user': friend_data
			}
		)


	async def remove_friend(self, friend_id):
		try:
			friendship = await database_sync_to_async(
				Friendship.objects.filter((
					Q(user_id=self.user_id, friend_id=friend_id) |
					Q(user_id=friend_id, friend_id=self.user_id)
				)).first
			)()
		except Friendship.DoesNotExist:
			logger.error(f'Error: cannot remove friendship between users')
			return

		await database_sync_to_async(friendship.delete)()
		logging.info(f'Friend removed')

		user_data = await self.get_user(self.user_id)
		friend_data = await self.get_user(friend_id)

		await self.channel_layer.group_send(
			f'user_{self.user_id}',
			{
				'type': 'friend_response',
				'action': 'friend_removed',
				'user': friend_data
			}
		)

		await self.channel_layer.group_send(
			f'user_{friend_id}',
			{
				'type': 'friend_response',
				'action': 'friend_removed',
				'user': user_data
			}
		)


	async def friend_response(self, event):
		action = event['action']
		user = event['user']

		await self.send(text_data=json.dumps({
			'action': action,
			'user': user
		}))

	async def get_user(self, user_id):
		try:
			async with httpx.AsyncClient() as client:
				token = create_jwt(self.user_id, timedelta(minutes=2))
				headers = {
					'Authorization': f'Bearer {token}'
				}
				response = await client.get(f"http://user-service:8000/api/users/{user_id}/", headers=headers)
				if response.status_code == 200:
					data = response.json()  # or use a custom user serializer
					return data.get('user')
				else:
					return None
		except httpx.RequestError as e:
			raise Exception(f"Error querying the user service: {str(e)}")