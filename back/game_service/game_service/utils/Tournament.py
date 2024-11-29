import logging
import asyncio
import typing
import math

from channels.db import database_sync_to_async
from game_service.models import GameModel

logger = logging.getLogger(__name__)

class Tournament():
	def __init__(self, tournament_id):
		self.tournament_id = tournament_id
		self.status = 'waiting'
		
		self.users = []

		self.game_tree = {}

		self.consumers = []


	def add_user(self, consumer):
		self.consumers.append(consumer)
		user_id = consumer.user_id

		if user_id not in self.users:
			self.users.append(user_id)


	def remove_user(self, consumer):
		user_id = consumer.user_id

		if user_id in self.users:
			self.users.remove(user_id)

		if consumer in self.consumers:
			self.consumers.remove(consumer)


	async def notify_users(self, user_ids, message):
		logger.info(f'users {user_ids}')
		for consumer in self.consumers:
			try:
				logger.info(f'user id {consumer.user_id}')
				if consumer.user_id not in user_ids:
					continue

				await consumer.send_json(message)

			except AttributeError as ae:
				logger.error(f'Consumer missing attributes user_id or send_json')
			except Exception as e:
				logger.error(f'Error will notifying the users')
	

	async def start(self):
		if self.status == 'started':
			return

		self.status = 'started'
		logger.info('Tournament started')

		rounds_number = math.ceil(math.log2(len(self.users)))
		current_users = self.users.copy()

		round_number = 1
		while len(current_users) > 1:
			logger.info(f'start')

			# create the games for the current round
			games = await self.create_round(current_users)
			self.game_tree[round_number] = games
			await self.send_tournament_tree()

			# wait 5 sec and notify users for their next game
			await asyncio.sleep(5)
			await self.send_game_id(games)

			logger.info(f'round created, waiting for winner')
			
			current_users = await self.wait(games)
			round_number += 1

			logger.info(f'some winners')

		logger.info(f'winner')


	async def create_round(self, users):
		games = []

		# Create games in pairs and store game IDs
		for i in range(0, len(users), 2):
			if i + 1 < len(users):
				game = await database_sync_to_async(
					GameModel.objects.create
				)(tournament_id=self.tournament_id)

				game.user_ids = [users[i], users[i + 1]]
				await database_sync_to_async(game.save)()
				games.append(game)

		return games


	async def wait(self, games):
		winners = []
		while len(winners) < len(games):
			await asyncio.sleep(1)
		
			# Check if all matches are finished
			for game in games:
				if await self.check_game_finished(game):
					winner_id = game.winner_id
					winners.append(winner_id)
			
		
		return winners


	async def check_game_finished(self, game):
		# Assume there's a method or a property in the Game model that checks if it's finished
		return game.status == 'finished'


	async def send_game_id(self, games):
		for game in games:
			await self.notify_users(game.user_ids, {
				'type': 'game_found',
				'id': game.id
			})


	async def send_tournament_tree(self):
	    """
	    Construct a serializable representation of the game tree.
	    :return: A dictionary representing the game tree.
	    """
	    tree = {}
	    for round_number, games in self.game_tree.items():
	        tree[round_number] = [
	            {"game_id": game.id, "user_ids": game.user_ids} for game in games
	        ]


	    await self.notify_users(self.users, {
			'type': 'tournament_info',
			'tournament': tree
		})
