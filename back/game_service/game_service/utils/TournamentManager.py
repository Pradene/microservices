from .Tournament import Tournament

class TournamentManager:
	_instance = None

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(TournamentManager, cls).__new__(cls, *args, **kwargs)
			cls._instance.tournaments = {}
		return cls._instance


	def get_tournament(self, tournament_id):
		return self.tournaments.get(tournament_id)


	def create_tournament(self, tournament_id):
		if tournament_id not in self.tournaments:
			tournament = Tournament(tournament_id)
			self.tournaments[tournament_id] = tournament
			return tournament

		else:
			return None  # Tournament already exists
