import logging
import typing
import json
import asyncio
import time
import math

from django.db import transaction
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from collections import deque

from game_service.utils import LocalGameManager
from game_service.models import Game

logger = logging.getLogger(__name__)

class LocalGameConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		self.user_id = self.scope['user_id']
		logging.info(f'user {self.user_id} connected to Game WebSocket')

		self.game_mode = self.scope['url_route']['kwargs']['game_mode']
		self.game_id = self.scope['url_route']['kwargs']['game_id'] if self.game_mode == 'remote' else '0'

		if self.game_mode != 'remote' and self.game_mode != 'local':
			logger.error(f'Wrong game mode, must be local or remote')
			await self.close()

		logger.info(f'game mode: {self.game_mode}')

		if self.user_id:
			await self.accept()

		else:
			await self.close()


	async def disconnect(self, close_code):
		pass


	async def receive(self, text_data):
		try:
			data = json.loads(text_data)
			logger.info(f'data received: {data}')
			
			message_type = data.get('type')

			if not self.is_user_in_game():
				return

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
			key = f'game:{self.game_id}:users'
			users = cache.get(key, {})
			users[self.user_id] = self.user_id
			cache.set(key, users, timeout=None)
		
		await self.start_game_if_ready()


	async def handle_user_update(self, data):
		user_id = data.get('user_id')
		movement = data.get('movement')

		self.game_manager.update_user(user_id, movement)


	async def start_game_if_ready(self):
		logger.info(f'start game in {self.game_mode}')

		if self.game_mode == 'local':
			self.game_manager = LocalGameManager(
				self.game_mode,
				self.game_id,
				[self.user_id, 0]
			)
			
			self.game_manager.add_observer(self)
			asyncio.create_task(self.game_manager.start_game())
		
		elif self.game_mode == 'remote':
			return


	async def is_user_in_game(self):
		''' Check if the current user is in the game. '''
		return await database_sync_to_async(
			Game.objects
			.filter(id=self.game_id, user_ids__contains=[self.user_id])
			.exists
		)()


	async def send_game_state(self, game_state):
		if self.game_mode == 'remote':
			await self.channel_layer.group_send(
				self.group_name,
				{
					'type': 'send_game',
					'data': game_state
				}
			)

		elif self.game_mode == 'local':
			await self.channel_layer.send(
				self.channel_name,
				{
					'type': 'send_game',
					'data': game_state
				}
			)

	async def send_game(self, event):
		data = event.get('data')

		if data['status'] == 'waiting':
			await self.send_json(data)

		elif data['status'] == 'started' or data['status'] == 'finished':
			users = data['users']
			ball = data['ball']
			player = users.get(str(self.user_id))

			opponent = next(
				(user for user_id, user in users.items() if user_id != str(self.user_id)),
				None
			)

			if opponent and opponent['id'] == self.user_id:
				opponent = None

			if player and player['position']['x'] < 0:
				opponent['position']['x'] = -opponent['position']['x']
				player['position']['x'] = -player['position']['x']
				ball['position']['x'] = -ball['position']['x']

			await self.send_json({
				'status':   data['status'],
				'player':   player,
				'opponent': opponent,
				'ball':     ball
			})
