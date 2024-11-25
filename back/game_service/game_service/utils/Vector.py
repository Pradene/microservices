import math
import random
import logging

def generate_vector():
    number = random.uniform(-0.5, 0.5)
    return Vector2(1, number).normalize()

def generate_vector_in_direction(direction):
    number = random.uniform(-0.5, 0.5)

    if direction == 'left':
        return Vector2(-1, number).normalize()
    elif direction == 'right':
        return Vector2(1, number).normalize()
    else:
        return Vector2(1, number).normalize()

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self):
        len = self.length()
        if len != 0:
            self.x /= len
            self.y /= len
        return self

    def scale(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def distance_to(self, other):
        return (self - other).length()

    def reflect(self, normal):
        dot_product = self.dot(normal)
        return self - normal.scale(2 * dot_product)