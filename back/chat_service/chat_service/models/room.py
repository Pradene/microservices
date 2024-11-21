from django.db import models
from django.contrib.postgres.fields import ArrayField

class Room(models.Model):
	user_ids = ArrayField(models.IntegerField(), default=list)
	is_private = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def is_member(self, user_id):
		return user_id in self.user_ids
	