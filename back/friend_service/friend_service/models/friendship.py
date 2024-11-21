from django.db import models

class Friendship(models.Model):
	user_id = models.IntegerField()
	friend_id = models.IntegerField()

	STATUS_CHOICES = [
		('pending', 'Pending'),
		('accepted', 'Accepted'),
		('blocked', 'Blocked')
	]

	status = models.CharField(choices=STATUS_CHOICES, default='pending')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['user_id', 'friend_id'],
				name='unique_friendship'
			),
			models.CheckConstraint(
				check=~models.Q(user_id=models.F('friend_id')),
				name='prevent_self_friendship'
			)
		]

	def __str__(self):
		return f"Friendship: {self.user_id} -> {self.friend_id} ({self.status})"
