import logging
import typing
import json
import asyncio
import time
import math
import uuid

from django.db import transaction
from django.core.cache import cache
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from collections import deque

from game_service.utils import GameManager
from game_service.models import Game

logger = logging.getLogger(__name__)

class GameConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		self.user_id = self.scope['user_id']
		logging.info(f'user {self.user_id} connected to Game WebSocket')

		self.game_mode = self.scope['url_route']['kwargs']['game_mode']
		self.game_id = self.scope['url_route']['kwargs']['game_id'] if self.game_mode == 'remote' else '0'

		if self.game_mode != 'remote' and self.game_mode != 'local':
			logger.error(f'Wrong game mode, must be local or remote')
			await self.close()

		if self.user_id:
			await self.accept()

			self.game_manager = GameManager()

			if self.game_mode == 'remote':
				self.game = self.game_manager.get_game(self.game_id)
				if not self.game:
					self.game = self.game_manager.create_game(self.game_id)
			
			elif self.game_mode == 'local':
				self.game = self.game_manager.create_game()
				self.game.add_consumer()
				
			self.game.add_consumer(self)

		else:
			await self.close()


	async def disconnect(self, close_code):
		pass


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
				await self.game_manager.quit(self.user_id)

		except Exception as e:
			logging.error(f'error: {e}')


	async def handle_user_ready(self, data):
		if self.game_mode == 'remote':

			users_key = f'game:{self.game_id}:users'
			users = cache.get(users_key, [])

			if self.user_id not in users:
				users.append(self.user_id)
				cache.set(users_key, users, timeout=None)

			await self.channel_layer.group_add(
				f'game_{self.game_id}',
				self.channel_name
			)

			lock_key = f'game:{self.game_id}:lock'
			lock = cache.add(lock_key, str(uuid.uuid4()), timeout=60)

			if lock:
				try:
					if len(users) >= 2:
						await self.start_game()
				finally:
					cache.delete(lock_key)


		elif self.game_mode == 'local':
			await self.start_game()


	async def start_game(self):
		logger.info(f'start game in {self.game_mode}')
		asyncio.create_task(self.game.start_game())


	async def handle_user_update(self, data):
		user_id = data.get('user_id')
		movement = data.get('movement')

		self.game.update_user(user_id, movement)


	async def is_user_in_game(self):
		''' Check if the current user is in the game. '''
		return await database_sync_to_async(
			Game.objects
			.filter(id=self.game_id, user_ids__contains=[self.user_id])
			.exists
		)()
