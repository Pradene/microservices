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

class LocalGameManager:
	def __init__(self, mode, id, user_ids):
		self.user_ids = list(user_ids)
		
		self.ball = Ball()
		self.users = {}
		self.countdown = COUNTDOWN

		self.status = 'waiting'
		self.state = self.initialize_state()

		logging.info(f'users {self.users}')
		
		self.observers = []


	def initialize_state(self):
		positions = {
			self.user_ids[0]: Vector2(-400 + 20, 0),
			self.user_ids[1]: Vector2(400 - 20, 0),
		}

		self.users = {user_id:
			Player(user_id, positions.get(user_id, Vector2(0, 0)))
		for user_id in self.user_ids}

		return {
			'status': self.status,
			'users': {
				str(user_id): {
					'id': self.users[user_id].id,
					'position': self.users[user_id].position,
					'score': self.users[user_id].score,
				} for user_id in self.user_ids
			},
			'ball': str(self.ball.position),
		}


	def add_observer(self, observer):
		self.observers.append(observer)


	def remove_observer(self, observer):
		self.observers.remove(observer)


	async def notify_observers(self):
		game_state = self.get_game_state()
		for observer in self.observers:
			await observer.send_game_state(game_state)


	async def start_game(self):
		try:
			logging.info("Starting game")

			while self.countdown >= 0:
				await self.notify_observers()
				await asyncio.sleep(1)
				self.countdown -= 1

			self.status = 'started'
			await self.notify_observers()

			last_frame = time.time()
			while self.status != 'finished':
				
				for user_id, user in self.users.items():
					user.move()

				self.ball.move()

				await self.check_collisions()

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

		for user in self.users.values():
			collision_normal = line_rect_collision(self.ball.position, future_position, user)
			if collision_normal:
				# Reflect the ball's direction based on the collision normal
				self.ball.direction = self.ball.direction.reflect(collision_normal)
				self.ball.increase_speed()
				break


	async def check_wall_collisions(self, start, end):
		# Check collision with left wall
		if line_intersection(start, end, Vector2(-400, 300), Vector2(-400, -300)):
			user = self.get_user_by_x_position(400 - 20)
			user.score += 1

			if await self.check_game_finished():
				return None

			asyncio.create_task(self.ball.reset(direction='left'))
			return None

		# Check collision with right wall
		if line_intersection(start, end, Vector2(400, 300), Vector2(400, -300)):
			user = self.get_user_by_x_position(-400 + 20)
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


	def get_game_state(self):
		status = self.status

		data = {
			'status': status,
			'users': {
				str(user_id): self.get_user_info(user_id)
				for user_id in self.user_ids
			},
			'ball': {
				'position': {
					'x': self.ball.position.x,
					'y': self.ball.position.y
				}
			}
		}

		if status == 'waiting':
			data['timer'] = self.countdown

		return data
