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

logger = logging.getLogger(__name__)

class Game:
	def __init__(self):
		self.countdown = COUNTDOWN
		self.status = 'waiting'

		self.ball = Ball()

		self.users = {}
		self.consumers = []


	def add_consumer(self, consumer=None):
		if consumer is None:
			user_id = 0
		else:
			self.consumers.append(consumer)
			user_id = consumer.user_id

		self.users[user_id] = Player(user_id, self.get_initial_pos())


	def get_initial_pos(self):
		positions = [
			Vector2((400 - 20), 0),
			Vector2(-(400 - 20), 0),
		]

		if len(self.users) < len(positions):
			return positions[len(self.users)]
		else:
			return None

	def remove_consumer(self, consumer):
		self.consumers.remove(consumer)


	async def notify_players(self):
		for consumer in self.consumers:
			game_state = self.get_game_state(consumer.user_id)
			await consumer.send_json(game_state)


	async def start_game(self):
		try:
			logging.info("Starting game")

			while self.countdown >= 0:
				await self.notify_players()
				await asyncio.sleep(1)
				self.countdown -= 1

			self.status = 'started'
			await self.notify_players()

			last_frame = time.time()
			while self.status != 'finished':
				
				for user_id, user in self.users.items():
					user.move()

				self.ball.move()

				await self.check_collisions()

				await self.notify_players()

				current_frame = time.time()
				if current_frame - last_frame < TIME_TO_SLEEP:
					await asyncio.sleep(TIME_TO_SLEEP - (current_frame - last_frame))
				
				last_frame = current_frame

			await self.notify_players()


		except Exception as e:
			logging.error(f'error: {e}')


	async def check_collisions(self):
		future_position = self.ball.position + self.ball.direction.scale(self.ball.speed)

		collision_normal = await self.check_wall_collisions(self.ball.position, future_position)
		if collision_normal:
			# Reflect the ball's direction based on wall collision
			self.ball.direction = self.ball.direction.reflect(collision_normal)
			return

		for user in self.users.values():
			direction = line_rect_collision(self.ball.position, future_position, user)
			if direction:
				# Reflect the ball's direction based on the collision normal
				self.ball.direction = direction
				self.ball.increase_speed()
				break


	async def check_wall_collisions(self, start, end):
		# Check collision with left wall
		if line_intersection(start, end, Vector2(-400, 300), Vector2(-400, -300)):
			user = self.get_user_by_x_position((400 - 20))
			user.score += 1

			if await self.check_game_finished():
				return None

			asyncio.create_task(self.ball.reset(direction='left'))
			return None

		# Check collision with right wall
		if line_intersection(start, end, Vector2(400, 300), Vector2(400, -300)):
			user = self.get_user_by_x_position(-(400 - 20))
			user.score += 1

			if await self.check_game_finished():
				return None

			asyncio.create_task(self.ball.reset(direction='right'))
			return None
		
		# Check collision with top wall
		if line_intersection(start, end, Vector2(-400, 300), Vector2(400, 300)):
			return Vector2(0, 1)  # Collision normal facing down
		# Check collision with bottom wall
		if line_intersection(start, end, Vector2(-400, -300), Vector2(400, -300)):
			return Vector2(0, -1)  # Collision normal facing up
		
		return None

	async def check_game_finished(self):
		finished = False
		for user in self.users.values():
			if user.score >= POINTS_TO_WIN:
				self.status = 'finished'
				return True
		
		return False

	def get_user_by_x_position(self, x_position):
		# Find and return the user with the specified `pos_x` value
		for user_id, user in self.users.items():
			if user.position.x == x_position:
				return user
		return None


	def update_user(self, user_id, movement):
		user = self.users.get(user_id)
		user.setMovement(movement)


	async def quit(self, user_id):
		self.status = 'finished'


	def get_user_info(self, user_id):
		user = self.users.get(user_id)
		return {
			'id': user_id,
			'score': user.score,
			'position': {
				'x': user.position.x,
				'y': user.position.y
			}
		} if user else None


	def get_game_state(self, user_id):
		if user_id is None:
			return

		player_info = self.get_user_info(user_id)
		opponent_id = next((uid for uid in self.users.keys() if uid != user_id), None)
		opponent_info = self.get_user_info(opponent_id) if opponent_id is not None else None

		data = {
			'status': self.status,
			'player': player_info,
			'opponent': opponent_info,
			'ball': {
				'position': {
					'x': self.ball.position.x,
					'y': self.ball.position.y
				}
			}
		}

		if self.status == 'waiting':
			data['timer'] = self.countdown

		return data
