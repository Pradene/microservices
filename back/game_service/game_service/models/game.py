from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import ArrayField

class GameModel(models.Model):
	status = models.CharField(choices=[
		('waiting', 'Waiting'),
		('ready', 'Ready'),
		('started', 'Started'),
		('paused', 'Paused'),
		('finished', 'Finished')
	], default='waiting')
	user_ids = ArrayField(models.IntegerField(), default=list)
	winner_id = models.IntegerField(null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	tournament_id = models.IntegerField(blank=True, null=True)
	tournament_round = models.IntegerField(blank=True, null=True)

	def set_winner(self, user_id):
		if user_id in self.user_ids:
			self.winner_id = user_id
			self.status = 'finished'
			self.save()

	def is_finished(self):
		return self.status == 'finished'

	def toJSON(self):
		players = [{
			'id': score.user_id,
			# 'picture': score.player.picture.url if score.player.picture else None,
			# 'username': score.player.username,
			'score': score.score
		} for score in self.scores.all()]

		data = {
			'id': self.id,
			'status': self.status,
			'tournament': self.tournament_id,
			'winner_id': self.winner_id,
			# 'users': players
		}

		return data

class ScoreModel(models.Model):
	game_id = models.IntegerField()
	user_id = models.IntegerField()
	score = models.IntegerField(default=0)

	class Meta:
		unique_together = ('game_id', 'user_id')

	def __str__(self):
		return f'user_id {self.user_id} scored {self.score} points in game {self.game_id}'

	def toJSON(self):
		return {
			'user_id': self.user_id,
			'score': self.score
		}