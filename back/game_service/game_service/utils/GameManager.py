from .Game import Game

class GameManager:
	_instance = None

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(GameManager, cls).__new__(cls, *args, **kwargs)
			cls._instance.games = {}
		return cls._instance


	def get_game(self, game_id):
		return self.games.get(game_id)


	def create_game(self, game_id=None):
		if game_id is None:
			return Game()

		if game_id not in self.games:
			game = Game(game_id)
			self.games[game_id] = game
			return game

		else:
			return None  # Game already exists
