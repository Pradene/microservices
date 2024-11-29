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

from game_service.models import GameModel

TIME_TO_SLEEP: float = (1 / FPS)

logger = logging.getLogger(__name__)

class Game:
	def __init__(self, game_id=None):
		self.game_id = game_id
		self.status = 'waiting'
		self.countdown = COUNTDOWN

		self.ball = Ball()

		self.users = {}
		self.active_users = {}

		self.consumers = []

		self.pause_timer = None
		self.pause_user_id = None
		self.winner_id = None


	def add_user(self, consumer=None):
		if consumer is None:
			user_id = 0
		else:
			self.consumers.append(consumer)
			user_id = consumer.user_id

		if user_id not in self.users:
			self.users[user_id] = Player(user_id, self.get_initial_pos())
		
		self.active_users[user_id] = True


	def get_initial_pos(self):
		positions = [
			Vector2((400 - 20), 0),
			Vector2(-(400 - 20), 0),
		]

		if len(self.users) < len(positions):
			return positions[len(self.users)]
		else:
			return None


	def remove_user(self, consumer):
		self.consumers.remove(consumer)
		user_id = consumer.user_id

		if user_id in self.active_users:
			self.active_users[user_id] = False


	async def notify_users(self):
		for consumer in self.consumers:
			game_state = self.get_game_state(consumer.user_id)
			await consumer.send_json(game_state)


	async def start(self):
		try:
			if self.status != 'waiting':
				return

			self.status = 'ready'

			while self.countdown >= 0:
				await self.notify_users()
				await asyncio.sleep(1)
				self.countdown -= 1

			self.status = 'started'
			await self.notify_users()

			last_frame = time.time()
			while self.status != 'finished':

				if self.status == 'paused':
					self.pause_timer = self.pause_timer - 0.1
					if self.pause_timer <= 0:
						self.status = 'started'
					await asyncio.sleep(0.1)
					continue
				
				for user_id, user in self.users.items():
					user.move()

				self.ball.move()

				await self.check_collisions()
				await self.notify_users()

				current_frame = time.time()
				if current_frame - last_frame < TIME_TO_SLEEP:
					await asyncio.sleep(TIME_TO_SLEEP - (current_frame - last_frame))
				
				last_frame = current_frame

			await self.save_game(self.winner_id)
			await self.notify_users()


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


	async def pause(self, user_id):
		if self.status != 'started':
			return

		self.status = 'paused'
		self.pause_timer = PAUSE_TIMER
		self.pause_user_id = user_id

		logger.info(f'pause game by {user_id}')
		await self.notify_users()


	async def unpause(self, user_id=None):
		if self.status != 'paused':
			return

		if user_id and user_id != self.pause_user_id:
			return

		self.status = 'started'
		self.pause_timer = None
		self.pause_user_id = None

		logger.info(f'unpause the game')
		await self.notify_users()


	async def quit(self, user_id):
		logger.info(f'game quit')
		self.active_users[user_id] = False

		if self.game_id is not None:
			remaining_user_id = self.get_active_user_id()
			if remaining_user_id is not None:
				self.status = 'finished'
				await self.save_game(remaining_user_id)
	
	async def save_game(self, winner_id):
		try:
			game = await database_sync_to_async(
				GameModel.objects.get
			)(id=self.game_id)
			game.winner_id = winner_id
			game.status = 'finished'
			await database_sync_to_async(game.save)()
		
		except GameModel.DoesNotExist:
			logger.error(f'Game {self.game_id} does not exist')
		except Exception as e:
			logger.error(f'Cannot save game: {e}')


	async def check_game_finished(self):
		finished = False
		for user in self.users.values():
			if user.score >= POINTS_TO_WIN:
				self.status = 'finished'
				self.winner_id = user.id
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


	def get_active_users_count(self):
		return list(self.active_users.values()).count(True)


	def get_active_user_id(self):
		# Filter active users
		active_user_ids = [user_id for user_id, active in self.active_users.items() if active]

		# Return the single active user if only one remains
		if len(active_user_ids) == 1:
			return active_user_ids[0]  # Return the Player object
		return None  # Return None if no user or more than one user is active


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

		if self.status == 'ready':
			data['timer'] = self.countdown

		return data
