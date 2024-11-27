import typing
import logging

from .defines import *
from .Vector import Vector2


class Player:
    def __init__(self, id, position):
        self.id = id
        self.position = position
        self.movement = 'NONE'
        self.score = 0

    def setMovement(self, movement):
        if movement != "UP" and movement != "DOWN" and movement != "NONE":
            raise ValueError(f"Invalid movement: {movement}")
        
        self.movement = movement

    def move(self):
        speed = PADDLE_SPEED
        if self.movement == "UP":
            self.position.y -= speed
            if self.position.y < -300 + PADDLE_HEIGHT / 2:
                self.position.y = -300 + PADDLE_HEIGHT / 2
        elif self.movement == "DOWN":
            self.position.y += speed
            if self.position.y > 300 - PADDLE_HEIGHT / 2:
                self.position.y = 300 - PADDLE_HEIGHT / 2

    def get_bound(self):
        width = PADDLE_WIDTH
        height = PADDLE_HEIGHT
        
        return {
            'left': self.position.x - width / 2,
            'right': self.position.x + width / 2,
            'top': self.position.y - height / 2,
            'bottom': self.position.y + height / 2,
        }
