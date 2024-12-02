from typing import List

P1_POSITION: List[int] = [-(400 - 20), 0]
P2_POSITION: List[int] = [(400 - 20), 0]
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600

COUNTDOWN: int = 3

BALL_SIZE: int = 4
BALL_SPEED: int = 4
BALL_SPEED_INCREMENT: float = .3
BALL_BASE_POSITION: List[int] = [400 - 2, 300 - 2]
BALL_MIN_SIN: float = 0.2
BALL_MAX_SIN: float = 0.8

PADDLE_SPEED: int = 6
PADDLE_WIDTH: int = 8
PADDLE_HEIGHT: int = 64

POINTS_TO_WIN: int = 10

FPS: int = 60

PAUSE_TIMER: float = 30.0  # Pause timer in sec

TOURNAMENT_USERS_NUMBER = 4