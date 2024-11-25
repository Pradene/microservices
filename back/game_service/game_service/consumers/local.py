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

class LocalGameConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		self.user_id = self.scope['user_id']
		logging.info(f'user id: {self.user_id}')

		await self.accept()
		
		self.game_manager = LocalGameManager()
		self.game_manager.add_observer(self)
		asyncio.create_task(self.game_manager.start_game())

	async def disconnect(self, close_code):
		pass
		
	async def receive(self, text_data):
		try:
			data = json.loads(text_data)
			logging.info(f'data: {data}')

			if not self.game_manager:
				return

			if 'movement' in data:
				self.game_manager.update_player(self.user_id, data['movement'])
			elif 'p2movement' in data:
				self.game_manager.update_player(self.local_user.id, data['p2movement'])
			elif data['quit']:
				await self.game_manager.quit(self.user_id)

		except Exception as e:
			logging.error(f'error: {e}')

	async def is_user_in_game(self):
		''' Check if the current user is in the game. '''
		return await database_sync_to_async(
			Game.objects
			.filter(id=self.game_id, user_ids__contains=[self.user_id])
			.exists
		)()

	def get_connected_users(self):
		"""Return the list of connected users for the current game."""
		return list(self.connected_users.get(self.game_id, []))

	def add_connected_user(self, user, game_id):
		if game_id not in self.connected_users:
			self.connected_users[game_id] = set()
		self.connected_users[game_id].add(user)

	def remove_connected_user(self, user, game_id):
		if game_id in self.connected_users and user in self.connected_users[game_id]:
			self.connected_users[game_id].remove(user)
			# Clean up if no users are connected
			if not self.connected_users[game_id]:
				del self.connected_users[game_id]

	def check_users_connected(self):
		# Check if both players are connected
		with transaction.atomic():
			game = Game.objects.select_for_update().get(id=self.game_id)

			if game.status == 'waiting':
				players_count = game.players.count()
				connected_players = self.connected_users.get(self.game_id, set())

				if len(connected_players) == players_count:
					game.status = 'started'
					game.save()
					return True
		return False

	# async def send_username(self):
	#     users = await database_sync_to_async(list)(self.game.players.all())

	#     player = next((user for user in users if user.id == self.user.id), None)
	#     opponent = next((user for user in users if user.id != self.user.id), None)

	#     await self.send_json({
	#         'type':     'player_info',
	#         'player':   player.username,
	#         'opponent': opponent.username
	#     })

	async def send_game_state(self, game_state):
		logging.info(f'sending game')
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
			players = data['players']
			ball = data['ball']
			player = players.get(self.user.id)

			opponent = next(
				(p for user_id, p in players.items() if user_id != self.user.id),
				None
			)

			if opponent and opponent['id'] == self.user.id:
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

