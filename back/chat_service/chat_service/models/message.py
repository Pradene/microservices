from django.db import models

class Message(models.Model):
    user_id = models.IntegerField()
    room_id = models.IntegerField()
    content = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)