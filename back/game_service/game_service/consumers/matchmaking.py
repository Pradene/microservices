import logging
import typing
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from collections import deque

from game_service.utils.GameManager import GameManager
from game_service.utils.defines import *
from game_service.models import Game, Tournament

logger = logging.getLogger(__name__)

class MatchmakingConsumer(AsyncJsonWebsocketConsumer):
	tournament_queue = deque()
	game_queue = deque()
	channels = {}

	async def connect(self):
		self.user_id = self.scope['user_id']

		if self.user_id:
			self.type = self.scope['url_route']['kwargs']['type']

			await self.channel_layer.group_add(
				f'matchmaking_pool',
				self.channel_name
			)

			self.channels[self.user_id] = self.channel_name

			await self.accept()

			logging.info(f'type: {self.type}')

			if self.type == 'game':
				await self.join_game_queue()

			elif self.type == 'tournament':
				await self.join_tournament_queue()

		else:
			await self.close()


	async def disconnect(self, close_code):
		await self.channel_layer.group_discard(
			f'matchmaking_pool',
			self.channel_name
		)

		if self.user_id in self.game_queue:
			self.game_queue.remove(self.user_id)
		if self.user_id in self.tournament_queue:
			self.tournament_queue.remove(self.user_id)


	async def receive(self, text_data):
		data = json.loads(text_data)
		logging.info(data)


	async def join_tournament_queue(self):
		if self.user_id not in self.tournament_queue:
			self.tournament_queue.append(self.user_id)
			await self.join_tournament()

		else:
			logging.error('user is already in queue')

	async def join_tournament(self):
		if len(self.tournament_queue) >= 4:
			tournament = await database_sync_to_async(
				Tournament.objects.create
			)()

			player1 = self.tournament_queue.popleft()
			player2 = self.tournament_queue.popleft()
			player3 = self.tournament_queue.popleft()
			player4 = self.tournament_queue.popleft()

			# await database_sync_to_async(
			# 	tournament.players.add
			# )(player1, player2, player3, player4)

			# await self.tournament_found(player1.id, tournament.id)
			# await self.tournament_found(player2.id, tournament.id)
			# await self.tournament_found(player3.id, tournament.id)
			# await self.tournament_found(player4.id, tournament.id)

	async def tournament_found(self, user_id, tournament_id):
		channel_name = self.channels.get(user_id)
		if not channel_name:
			return

		await self.channel_layer.send(
			channel_name,
			{
				'type': 'tournament_found_response',
				'tournament_id': tournament_id
			}
		)

	async def tournament_found_response(self, data):
		tournament_id = data.get('tournament_id')
		
		await self.send_json({
			'type': 'tournament_found',
			'tournament_id': tournament_id
		})

	
	async def join_game_queue(self):
		if self.user_id not in self.game_queue:
			self.game_queue.append(self.user_id)
			await self.join_game()

		else:
			logging.error('user is already in queue')

	async def join_game(self):
		if len(self.game_queue) >= 2:
			game = await database_sync_to_async(
				Game.objects.create
			)()

			p1_id = self.game_queue.popleft()
			p2_id = self.game_queue.popleft()

			game.user_ids += [p1_id, p2_id]
			await database_sync_to_async(game.save)()

			await self.game_found(p1_id, game.id)
			await self.game_found(p2_id, game.id)


	async def game_found(self, user_id, game_id):
		channel_name = self.channels.get(user_id)
		if not channel_name:
			return

		await self.channel_layer.send(
			channel_name,
			{
				'type': 'game_found_response',
				'game_id': game_id
			}
		)

	async def game_found_response(self, data):
		game_id = data.get('game_id')
		
		await self.send_json({
			'type': 'game_found',
			'game_id': game_id
		})