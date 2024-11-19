from django.db import models

class Message(models.Model):
    user = models.IntegerField()
    room = models.IntegerField()
    content = models.CharField()