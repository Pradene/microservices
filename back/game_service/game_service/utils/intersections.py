from .Vector import Vector2
from .defines import *

def line_rect_collision(start, end, player):
    # Define the four edges of the player's rectangle
    rect_left = player.position.x - PADDLE_WIDTH / 2
    rect_right = player.position.x + PADDLE_WIDTH / 2
    rect_top = player.position.y - PADDLE_HEIGHT / 2
    rect_bottom = player.position.y + PADDLE_HEIGHT / 2
    # Check for intersection with each side and return the normal vector

    if line_intersects_line(start, end, Vector2(rect_left, rect_top), Vector2(rect_right, rect_top)):
        return Vector2(0, 1)  # Top collision normal
    if line_intersects_line(start, end, Vector2(rect_left, rect_bottom), Vector2(rect_right, rect_bottom)):
        return Vector2(0, -1)   # Bottom collision normal
    if line_intersects_line(start, end, Vector2(rect_left, rect_top), Vector2(rect_left, rect_bottom)):
        return Vector2(-1, 0)  # Left collision normal
    if line_intersects_line(start, end, Vector2(rect_right, rect_top), Vector2(rect_right, rect_bottom)):
        return Vector2(1, 0)   # Right collision normal
    return None  # No collision detected


def line_intersects_line(p1, p2, q1, q2):
    # Helper function to check if two line segments (p1-p2 and q1-q2) intersect
    def ccw(A, B, C):
        return (C.y - A.y) * (B.x - A.x) > (B.y - A.y) * (C.x - A.x)

    return (ccw(p1, q1, q2) != ccw(p2, q1, q2)) and (ccw(p1, p2, q1) != ccw(p1, p2, q2))