from .Vector import Vector2
from .defines import *

def line_rect_collision(start, end, player):
	# Define the four edges of the player's rectangle
	rect_left = player.position.x - PADDLE_WIDTH / 2
	rect_right = player.position.x + PADDLE_WIDTH / 2
	rect_top = player.position.y - PADDLE_HEIGHT / 2
	rect_bottom = player.position.y + PADDLE_HEIGHT / 2

	# Ball's current direction
	direction = end - start
	direction.normalize()

	# Check for collision with paddle edges
	intersection = None
	if intersection := line_intersection(start, end, Vector2(rect_left, rect_top), Vector2(rect_left, rect_bottom)):
		direction.x *= -1  # Reverse x-direction for left collision
	elif intersection := line_intersection(start, end, Vector2(rect_right, rect_top), Vector2(rect_right, rect_bottom)):
		direction.x *= -1  # Reverse x-direction for right collision
	elif intersection := line_intersection(start, end, Vector2(rect_left, rect_top), Vector2(rect_right, rect_top)):
		direction.y *= -1  # Reverse y-direction for top collision
	elif intersection := line_intersection(start, end, Vector2(rect_left, rect_bottom), Vector2(rect_right, rect_bottom)):
		direction.y *= -1  # Reverse y-direction for bottom collision

	# If collision with top or bottom, adjust y based on intersection position
	if intersection and (direction.y < 0 or direction.y > 0):
		# Relative position of the intersection along the paddle's width
		relative_y = (intersection.y - rect_top) / PADDLE_HEIGHT
		offset = (relative_y - 0.5) * 2  # Range: -1 to 1
		direction.y = offset * 0.5  # Adjust y-component based on offset
		direction.normalize()  # Re-normalize after modification

	return direction if intersection else None  # Return new direction or None if no collision


def line_intersection(p1, p2, q1, q2):
	"""Find the intersection point of two line segments if it exists."""
	def determinant(a, b, c, d):
		return a * d - b * c

	denom = determinant(p2.x - p1.x, q1.x - q2.x, p2.y - p1.y, q1.y - q2.y)
	if denom == 0:
		return None  # Parallel lines or coincident

	t = determinant(q1.x - p1.x, q1.x - q2.x, q1.y - p1.y, q1.y - q2.y) / denom
	u = determinant(p2.x - p1.x, q1.x - p1.x, p2.y - p1.y, q1.y - p1.y) / denom
	if 0 <= t <= 1 and 0 <= u <= 1:
		# Intersection point
		return Vector2(p1.x + t * (p2.x - p1.x), p1.y + t * (p2.y - p1.y))
	return None