import logging
import time
import asyncio
import typing

from channels.db import database_sync_to_async

from typing import List, Dict, Union, Callable

from .Ball import Ball
from .Player import Player
from .defines import *
from .Vector import Vector2
from .intersections import *

from game_service.models import Score, Game

TIME_TO_SLEEP: float = (1 / FPS)

class LocalGameManager:
	def __init__(self):
		self.ball = Ball()
		self.players = {}
		self.observers = []
		self.countdown = COUNTDOWN

	#     self.initialize_players()

	# def initialize_players(self):
	#     positions = {
	#         0: -400 + 20,
	#         1: 400 - 20
	#     }

	#     for i in enumerate(self.users):
	#         player = Player(
	#             id=user.id,
	#             name=user.username,
	#             position=Vector2(positions[i], 0)
	#         )
	#         self.players[user.id] = player


	def add_observer(self, observer: 'GameConsumer'):
		self.observers.append(observer)


	def remove_observer(self, observer: 'GameConsumer'):
		self.observers.remove(observer)


	async def notify_observers(self):
		game_state = {}
		# game_state = self.get_game_state()
		for observer in self.observers:
			# logging.info(f'Sending game state to observer {game_state}')
			await observer.send_game_state(game_state)


	async def start_game(self):
		try:
			logging.info("Starting local game")

			while self.countdown >= 0:
				await self.notify_observers()
				await asyncio.sleep(1)
				self.countdown -= 1

			# self.game.status = 'started'
			# await self.notify_observers()

			last_frame = time.time()
			# while self.game.status != 'finished':
			while True:
				
				# for user_id, player in self.players.items():
				# 	player.move()

				# if self.ball.moving:
					# self.ball.move()

				# await self.check_collisions()

				await self.notify_observers()

				current_frame = time.time()
				if current_frame - last_frame < TIME_TO_SLEEP:
					await asyncio.sleep(TIME_TO_SLEEP - (current_frame - last_frame))
				
				last_frame = current_frame

			await self.notify_observers()


		except Exception as e:
			logging.error(f'error: {e}')


	async def check_collisions(self):
		future_position = self.ball.position + self.ball.direction.scale(self.ball.speed)

		collision_normal = await self.check_wall_collisions(self.ball.position, future_position)
		if collision_normal:
			# Reflect the ball's direction based on wall collision
			self.ball.direction = self.ball.direction.reflect(collision_normal)
			return

		for player in self.players.values():
			collision_normal = line_rect_collision(self.ball.position, future_position, player)
			if collision_normal:
				# Reflect the ball's direction based on the collision normal
				self.ball.direction = self.ball.direction.reflect(collision_normal)
				break


	async def check_wall_collisions(self, start, end):
		# Check collision with left wall
		if line_intersects_line(start, end, Vector2(-400, 300), Vector2(-400, -300)):
			player = self.get_player_by_x_position(400 - 20)
			self.players[player.id].score += 1

			if await self.check_game_finished():
				return None

			asyncio.create_task(self.ball.reset(direction='left'))
			return None

		# Check collision with right wall
		if line_intersects_line(start, end, Vector2(400, 300), Vector2(400, -300)):
			player = self.get_player_by_x_position(-400 + 20)
			self.players[player.id].score += 1

			if await self.check_game_finished():
				return None

			asyncio.create_task(self.ball.reset(direction='right'))
			return None
		
		# Check collision with top wall
		if line_intersects_line(start, end, Vector2(-400, 300), Vector2(400, 300)):
			return Vector2(0, 1)  # Collision normal facing down
		# Check collision with bottom wall
		if line_intersects_line(start, end, Vector2(-400, -300), Vector2(400, -300)):
			return Vector2(0, -1)  # Collision normal facing up
		
		return None

	async def check_game_finished(self):
		finished = False
		for player in self.players.values():
			if player.score >= POINTS_TO_WIN:
				# Set the game status to finished and save the result to the database
				finished =  True
				user = await database_sync_to_async(
					CustomUser.objects.get
				)(id=player.id)

				await database_sync_to_async(user.add_xp)(10)

		if finished:
			for user in self.users:
				player = self.players.get(user.id)
				if player:
					await database_sync_to_async(
						Score.objects.create
					)(game=self.game, player=user, score=player.score)

				else:
					logging.info(f'No player found for user ID {user.id}')
				
			await database_sync_to_async(self.game.set_winner)()
			return True
		
		return False

	def get_player_by_x_position(self, x_position):
		# Find and return the player with the specified `pos_x` value
		for player in self.players.values():
			if player.position.x == x_position:
				return player
		return None


	def update_player(self, user_id, movement):
		player = self.players.get(user_id)
		player.setMovement(movement)


	async def quit(self, user_id):
		player = self.players.get(user_id)

		self.game.status = 'finished'
		await database_sync_to_async(
			self.game.save
		)()



	def get_player_info(self, user_id):
		player = self.players.get(user_id)
		return {
			'id': player.id,
			'score': player.score,
			'position': {
				'x': player.position.x,
				'y': player.position.y
			}
		} if player else None


	def get_game_state(self):
		status = self.game.status

		if status == 'waiting':
			return {
				'status': status,
				'timer': self.countdown
			}

		elif status == 'started' or status == 'finished':
			return {
				'status': status,
				'players': {
					user_id: self.get_player_info(user_id)
					for user_id in self.players
				},
				'ball': {
					'position': {
						'x': self.ball.position.x,
						'y': self.ball.position.y
					}
				}
			}

		else:
			return {
				'status': 'undefined'
			}
