from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import ArrayField

class TournamentModel(models.Model):
	user_ids = ArrayField(models.IntegerField(), default=list)

	def toJSON(self):
		games = Game.objects.all().filter(tournament_id=self.id).order_by('id')
		finished_games = games.filter(status='finished', tournament_id=self.id)

		winner_id = None
		try:
			winner_id = games[3].winner.toJSON()
		except Exception as e:
			pass

		return {
			'id': self.id,
			'players': [player.toJSON() for player in self.players.all()],
			'games': [game.toJSON() for game in games],
			'status': 'finished' if finished_games.count() == games.count() else 'started',
			'winner': winner
		}