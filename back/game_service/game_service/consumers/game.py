import logging
import typing
import json
import asyncio
import time
import math
import uuid
import httpx

from datetime import timedelta

from django.db import transaction
from django.core.cache import cache
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from collections import deque

from game_service.utils import GameManager, create_jwt
from game_service.models import GameModel

logger = logging.getLogger(__name__)

class GameConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		self.user_id = self.scope.get('user_id')
		logger.info(f'user {self.user_id} connected to Game WebSocket')

		self.game_mode = self.scope['url_route']['kwargs']['game_mode']
		self.game_id = self.scope['url_route']['kwargs']['game_id'] if self.game_mode == 'remote' else '0'

		if self.game_mode != 'remote' and self.game_mode != 'local':
			logger.error(f'Wrong game mode, must be local or remote')
			await self.close()

		if self.user_id:
			self.game_manager = GameManager()

			if self.game_mode == 'remote':
				try:
					game = await database_sync_to_async(
						GameModel.objects.get
					)(id=self.game_id)
				except GameModel.DoesNotExist:
					await self.close()
					return

				if game.status == 'finished':
					await self.close()
					return

				self.game = self.game_manager.get_game(self.game_id)
				if not self.game:
					self.game = self.game_manager.create_game(self.game_id)
				
				if self.game.status == 'finished':
					await self.close(4000)

				await self.channel_layer.group_add(
					f'game_{self.game_id}',
					self.channel_name
				)
			
			elif self.game_mode == 'local':
				self.game = self.game_manager.create_game()
				self.game.add_user()
				
			self.game.add_user(self)
			await self.accept()

		else:
			await self.close()


	async def disconnect(self, close_code):
		if self.user_id and self.game_mode == 'remote':
			await self.channel_layer.group_discard(
				f'game_{self.game_id}',
				self.channel_name
			)


	async def receive(self, text_data):
		try:
			data = json.loads(text_data)
			logger.info(f'data received: {data}')
			
			message_type = data.get('type')

			if message_type == 'ready':
				await self.handle_user_ready(data)
			elif message_type == 'update':
				await self.handle_user_update(data)
			elif message_type == 'quit':
				await self.handle_user_quit(self.user_id)
			elif message_type == 'pause':
				await self.handle_pause(self.user_id)
			elif message_type == 'unpause':
				await self.handle_unpause(self.user_id)

		except Exception as e:
			logger.error(f'error: {e}')


	async def handle_user_ready(self, data):
		if self.game_mode == 'remote':

			users_key = f'game:{self.game_id}:users'
			users = cache.get(users_key, [])

			if self.user_id not in users:
				users.append(self.user_id)
				cache.set(users_key, users, timeout=None)

			lock_key = f'game:{self.game_id}:lock'
			lock = cache.add(lock_key, str(uuid.uuid4()), timeout=60)

			if lock:
				try:
					if self.game.status == 'waiting' and len(users) >= 2:
						await self.start_game()
				finally:
					cache.delete(lock_key)

		elif self.game_mode == 'local':
			await self.start_game()


	async def send_users_info(self):
		users_key = f'game:{self.game_id}:users'
		users = cache.get(users_key, [])

		logger.info(f'users: {users}')

		users_data = []
		for user in users:
			user_info = await self.get_user(user)
			users_data.append(user_info)

		await self.channel_layer.group_send(
			f'game_{self.game_id}',
			{
				'type': 'users_info',
				'users': users_data
			}
		)

	async def users_info(self, event):
		await self.send_json(event)


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


	async def start_game(self):
		await self.send_users_info()
		asyncio.create_task(self.game.start())


	async def handle_user_update(self, data):
		user_id = data.get('user_id')
		movement = data.get('movement')

		self.game.update_user(user_id, movement)


	async def handle_user_quit(self, user_id):
		await self.game.quit(user_id)

		# Remove the other user from game if in local mode
		if self.game_mode == 'local':
			await self.game.quit(0)


	async def handle_pause(self, user_id):
		await self.game.pause(user_id)


	async def handle_unpause(self, user_id):
		await self.game.unpause(user_id)


	async def send_error(self, message):
		await self.send_json({
			'type': 'error',
			'message': message
		})


	async def is_user_in_game(self):
		''' Check if the current user is in the game. '''
		return await database_sync_to_async(
			Game.objects.filter(
				id=self.game_id,
				user_ids__contains=[self.user_id]
			).exists
		)()
