import random
import math
import logging
import asyncio

from .Player import Player
from .defines import *
from .Vector import *

class Ball:
    def __init__(self):
        self.position = Vector2(0, 0)
        self.direction = generate_vector()
        self.moving = True
        self.speed = BALL_SPEED

    async def reset(self, direction):
        self.position = Vector2(0, 0)
        self.direction = generate_vector_in_direction(direction)
        self.moving = False
        await asyncio.sleep(1)
        self.moving = True

    def move(self):
        self.position += self.direction.scale(self.speed)
