import logging
import asyncio
import typing
import math
import httpx

from datetime import timedelta

from channels.db import database_sync_to_async
from game_service.models import GameModel
from game_service.utils import create_jwt

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

		rounds_number = math.ceil(math.log2(len(self.users)))
		current_users = self.users.copy()

		round_number = 1
		while len(current_users) > 1:
			# create the games for the current round
			logger.info(f'Create tournament round')
			games = await self.create_round(current_users)
			self.game_tree[round_number] = games
			logger.info(self.game_tree)
			await self.send_tournament_tree()

			# wait 5 sec and notify users for their next game
			await asyncio.sleep(5)
			
			logger.info('sending game to users')
			await self.send_game_id(games)
			
			current_users = await self.wait(games)
			round_number += 1

		logger.info(f'tournament finished')
		await self.save_tournament()


	async def save_tournament(self):
		try:
			tournament = await database_sync_to_async(
				TournamentModel.objects.get
			)(id=self.tournament_id)
		except TournamentModel.DoesNotExist:
			return

		tournament.status = 'finished'
		await database_sync_to_async(tournament.save)()



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
				if await self.check_game_finished(game.id):
					winner_id = await self.get_game_winner(game.id)
					if winner_id not in winners:
						winners.append(winner_id)

		return winners


	async def check_game_finished(self, game_id):
		try:
			game = await database_sync_to_async(
				GameModel.objects.get
			)(id=game_id)
		except GameModel.DoesNotExist:
			return

		# Assume there's a method or a property in the Game model that checks if it's finished
		return game.status == 'finished'


	async def get_game_winner(self, game_id):
		try:
			game = await database_sync_to_async(
				GameModel.objects.get
			)(id=game_id, status='finished')
		except GameModel.DoesNotExist:
			return

		return game.winner_id
		

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
		users_data = {}
		for user_id in self.users:
			user_info = await self.get_user(user_id)
			if user_info:
				users_data[user_id] = user_info
				
		for round_number, games in self.game_tree.items():
			tree[round_number] = []
			for game in games:
				game_info = { "game_id": game.id }

				game_info['users'] = [
					{
						'id': user_id,
						'username': users_data.get(user_id).get('username'),
						'picture': users_data.get(user_id).get('picture'),
					} for user_id in game.user_ids
				]

				tree[round_number].append(game_info)

		await self.notify_users(self.users, {
			'type': 'tournament_info',
			'tournament': tree
		})


	async def get_user(self, user_id):
		try:
			async with httpx.AsyncClient() as client:
				token = create_jwt(user_id, timedelta(minutes=2))
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

