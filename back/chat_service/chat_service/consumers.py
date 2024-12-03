import asyncio
import typing
import json
import logging
import requests

from datetime import timedelta

from django.core.cache import cache
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async

from chat_service.models import Room, Message, Invitation
from chat_service.utils import create_jwt

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		self.user_id = self.scope.get('user_id')
		logging.info(f'user id: {self.user_id}')

		if self.user_id:
			cache.set(f'user{self.user_id}_chat_wschannel', self.channel_name, timeout=None)
			tmp = cache.get(f'user{self.user_id}_chat_wschannel')
			logger.info(f'channel_name of {self.user_id}: {tmp}')
			rooms = await self.get_rooms()
			for room in rooms:
				logger.info(f'Room ID: {room.id}')
				await self.channel_layer.group_add(
					f'chat_{room.id}',
					self.channel_name
				)

			await self.accept()

			logger.info(f'connected to chat consumer')

		else:
			await self.close()

	async def disconnect(self, close_code):
		if self.user_id:
			cache.delete(f'user{self.user_id}_chat_wschannel')
			rooms = await self.get_rooms()
			for room in rooms:
				await self.channel_layer.group_discard(
					f'chat_{room.id}',
					self.channel_name
				)


	async def receive(self, text_data):
		data = json.loads(text_data)
		logging.info(f"received: {data}")

		message_type = data.get('type')
		room_id = data.get('room_id')

		try:
			room = await database_sync_to_async(
				Room.objects.get
			)(id=room_id)
		except Room.DoesNotExist:
			logger.error(f'Error: room {room_id} does not exist')
			return

		is_member = await database_sync_to_async(room.is_member)(self.user_id)
		if not is_member:
			logging.error(f"{self.user_id} not in room {room.id}")
			return

		if message_type == 'send_message':
			await self.send_message(data)

		elif message_type == 'send_invitation':
			await self.send_invitation(data)

		elif message_type == 'cancel_invitation':
			await self.cancel_invitation(data)

		elif message_type == 'cancel_all_invitations':
			await self.cancel_all_invitations(data)

		elif message_type == 'decline_invitation':
			await self.decline_invitation(data)

		elif message_type == 'accept_invitation':
			await self.accept_invitation(data)


	async def send_invitation(self, data):
		try:
			room_id = int(data.get('room_id'))
			room = await database_sync_to_async(
				Room.objects.get
			)(id=room_id)

			existing_invitations = await database_sync_to_async(
				list
			)(Invitation.objects.filter(user_id=self.user_id, room_id=room_id, status='pending'))

			# Loop through each existing invitation
			for invitation in existing_invitations:
				invitation.status='canceled'
				await database_sync_to_async(invitation.save)()

				await self.channel_layer.group_send(
					f'chat_{room.id}',
					{
						'type': 'invitation',
						'id': invitation.id,
						'room_id': room_id,
						'user_id': self.user_id,
						'status': invitation.status,
					}
				)


			invitation = await database_sync_to_async(
				Invitation.objects.create
			)(room_id=room_id, user_id=self.user_id)

			logging.info(invitation)

			await self.channel_layer.group_send(
				f'chat_{room_id}',
				{
					'type': 'invitation',
					'id': invitation.id,
					'room_id': room_id,
					'user_id': self.user_id,
					'status': invitation.status,
				}
			)

		except Exception as e:
			logging.info(f'error {e}')


	async def cancel_invitation(self, data):
		try:
			room_id = int(data.get('room_id'))
			invitation_id = int(data.get('invitation_id'))

			room = await database_sync_to_async(
				Room.objects.get
			)(id=room_id)

			invitation = await database_sync_to_async(
				Invitation.objects.get
			)(id=invitation_id)

			if invitation.user_id != self.user_id:
				logger.error(f'Error: you cannot cancel an invitation from another user')
				return

			elif invitation.room_id != room_id:
				logger.error(f'Error: the invitation is not in the room {room_id}')
				return

			invitation.status = 'canceled'
			await database_sync_to_async(invitation.save)()

			await self.channel_layer.group_send(
				f'chat_{room_id}',
				{
					'type': 'invitation',
					'id': invitation.id,
					'room_id': room_id,
					'user_id': self.user_id,
					'status': invitation.status,
				}
			)

		except Exception as e:
			logging.error(f'error: {e}')


	async def cancel_all_invitations(self, data):
		try:
			room_id = int(data.get('room_id'))
			room = await database_sync_to_async(
				Room.objects.get
			)(id=room_id)

			existing_invitations = await database_sync_to_async(
				list
			)(Invitation.objects.filter(user_id=self.user_id, room_id=room.id, status='pending'))

			for invitation in existing_invitations:
				invitation.status='canceled'
				await database_sync_to_async(invitation.save)()

				await self.channel_layer.group_send(
					f'chat_{room.id}',
					{
						'type': 'invitation',
						'id': invitation.id,
						'room_id': room.id,
						'user_id': self.user_id,
						'status': invitation.status,
					}
				)

		except Exception as e:
			logging.error(f'error: {e}')


	async def decline_invitation(self, data):
		try:
			room_id = int(data.get('room_id'))
			invitation_id = int(data.get('invitation_id'))

			room = await database_sync_to_async(
				Room.objects.get
			)(id=room_id)

			invitation = await database_sync_to_async(
				Invitation.objects.get
			)(id=invitation_id)

			if invitation.user_id == self.user_id:
				return

			if invitation.room_id != room.id:
				return

			invitation.status = 'declined'
			await database_sync_to_async(invitation.save)()

			await self.channel_layer.group_send(
				f'chat_{room.id}',
				{
					'type': 'invitation',
					'id': invitation.id,
					'room_id': room.id,
					'user_id': invitation.user_id,
					'status': invitation.status,
				}
			)

		except Exception as e:
			logging.error(f'error: {e}')

	async def accept_invitation(self, data):
		try:
			room_id = int(data.get('room_id'))
			invitation_id = int(data.get('invitation_id'))

			room = await database_sync_to_async(
				Room.objects.get
			)(id=room_id)

			invitation = await database_sync_to_async(
				Invitation.objects.get
			)(id=invitation_id)

			if invitation.status != 'pending':
				return

			if invitation.user_id == self.user_id:
				return

			if invitation.room_id != room.id:
				return

			user_ids = [self.user_id, invitation.user_id]
			token = create_jwt(self.user_id, timedelta(minutes=2))
			response = await sync_to_async(requests.post)(
				f'http://game-service:8000/api/games/',
				json={'user_ids': user_ids},
				headers={'Authorization': f'Bearer {token}'},
			)

			if response.status_code == 200:
				data = response.json()
				game_id = data.get('game_id')
				
				invitation.status = 'accepted'
				await database_sync_to_async(invitation.save)()

				await self.channel_layer.group_send(
					f'chat_{room.id}',
					{
						'type': 'invitation',
						'id': invitation.id,
						'room_id': room.id,
						'user_id': invitation.user_id,
						'status': invitation.status,
						'game_id': game_id,
					}
				)

		except Exception as e:
			logging.error(f'error: {e}')


	async def invitation(self, data):
		await self.send_json(data)


	async def send_message(self, data):
		content = data.get('content')
		room_id = int(data.get('room_id'))

		try:
			message = await database_sync_to_async(
				Message.objects.create
			)(room_id=room_id, user_id=self.user_id, content=content)

			message_data = {
				'type': 'message',
				'room_id': message.room_id,
				'user_id': message.user_id,
				'content': message.content
			}

			await self.channel_layer.group_send(
				f'chat_{room_id}',
				message_data
			)

		except Exception as e:
			logger.error(f'Error: during send messsage, {str(e)}')
			return

	async def message(self, event):
		await self.send_json(event)


	# # get all rooms of an user
	@database_sync_to_async
	def get_rooms(self):
		rooms = Room.objects.filter(
			user_ids__contains=[self.user_id]
		)

		return list(rooms)

