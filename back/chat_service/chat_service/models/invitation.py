from django.db import models

class Invitation(models.Model):
	user_id = models.IntegerField()
	room_id = models.IntegerField()
	
	STATUS_CHOICES = [
		('pending', 'Pending'),
		('canceled', 'Canceled'),
		('accepted', 'Accepted'),
		('declined', 'Declined'),
	]
	
	status = models.CharField(choices=STATUS_CHOICES, default='pending')
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'Invitation from user {self.user_id} in room {self.room_id} is {self.status}'
