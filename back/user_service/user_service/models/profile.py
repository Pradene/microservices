from django.db import models

class Profile(models.Model):
    user_id = models.IntegerField(unique=True)
    username = models.CharField(max_length=32, unique=True)
    email = models.EmailField(max_length=255)
    picture = models.ImageField(upload_to="profile_pictures/", default="profile_pictures/default.png", blank=True, null=True)
    bio = models.CharField(max_length=255)
    level = models.PositiveIntegerField(default=1)
    experience = models.PositiveIntegerField(default=0)
    is_2fa_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.username
