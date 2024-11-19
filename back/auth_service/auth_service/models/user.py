from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
	username = models.CharField(max_length=32, unique=True)
	email = models.EmailField(max_length=255)
	id_42 = models.CharField(max_length=255, unique=True, null=True, blank=True)
	is_2fa_enabled = models.BooleanField(default=False)
	is_staff = models.BooleanField(default=False)
	is_online = models.BooleanField(default=False)

	def __str__(self):
		return self.username
