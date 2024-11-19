from django.db import models
from django.contrib.postgres.fields import ArrayField

class Room(models.Model):
	is_private = models.BooleanField(default=True)
	user_ids = ArrayField(models.PositiveBigIntegerField(), default=list)
	created_at = models.DateTimeField(auto_now_add=True)