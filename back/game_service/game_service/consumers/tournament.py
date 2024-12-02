import logging
import typing
import json
import asyncio
import time
import math
import uuid

from django.core.cache import cache
from django.db import transaction
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from collections import deque

from game_service.utils import GameManager
from game_service.utils import TournamentManager
from game_service.utils.defines import *

from game_service.models import GameModel, TournamentModel

logger = logging.getLogger(__name__)

class TournamentConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		self.user_id = self.scope.get('user_id')

		if self.user_id:
			self.tournament_id = self.scope['url_route']['kwargs']['tournament_id']
			
			try:
				tournament = await database_sync_to_async(
					TournamentModel.objects.get
				)(id=self.tournament_id)
			except TournamentModel.DoesNotExist:
				await self.close()
				return

			if tournament.status == 'finished':
				await self.close()
				return

			self.tournament_manager = TournamentManager()

			self.tournament = self.tournament_manager.get_tournament(self.tournament_id)
			if not self.tournament:
				self.tournament = self.tournament_manager.create_tournament(self.tournament_id)

			await self.channel_layer.group_add(
				f'tournament_{self.tournament_id}',
				self.channel_name
			)

			self.tournament.add_user(self)
			await self.accept()
		
		else:
			await self.close()


	async def disconnect(self, close_code):
		if self.user_id:
			await self.channel_layer.group_discard(
				f'tournament_{self.tournament_id}',
				self.channel_name
			)


	async def receive(self, text_data):
		data = json.loads(text_data)
		logger.info(f'Tournament consumer received: {data}')

		message_type = data.get('type')

		if message_type == 'ready':
			await self.handle_user_ready(data)


	async def handle_user_ready(self, data):
		users_key = f'tournament:{self.tournament_id}:users'
		users = cache.get(users_key, [])

		if self.user_id not in users:
			users.append(self.user_id)
			cache.set(users_key, users, timeout=None)

		lock_key = f'tournament:{self.tournament_id}:lock'
		lock = cache.add(lock_key, str(uuid.uuid4()), timeout=60)

		if lock:
			try:
				if self.tournament.status == 'waiting' and len(users) >= 2:
					await self.start_tournament()
			finally:
				cache.delete(lock_key)


	async def start_tournament(self):
		asyncio.create_task(self.tournament.start())


	async def send_game(self, game_id, action='action'):
		logging.info(f'game id: {game_id}')
		
		game = await database_sync_to_async(
			Game.objects.get
		)(id=game_id)

		players = await database_sync_to_async(
			list
		)(game.players.all())

		for player in players:
			await self.send_game_to_user(player.id, game_id, action)


	async def send_game_to_user(self, user_id, game_id, action='action'):
		channel_name = self.channels.get(user_id)
		if not channel_name:
			return

		await self.channel_layer.send(
			channel_name,
			{
				'type': 'game_found',
				'game_id': game_id,
				'action': action,
				'tournament_id': self.tournament.id
			}
		)

	async def game_found(self, data):
		await self.send_json(data)