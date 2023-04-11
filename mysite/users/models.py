from django.db import models

from django.contrib.auth.models import User

class Profile(models.Model):
    image = models.ImageField(default='profile.jpg', upload_to='profile_pictures')
    contact_number = models.CharField(max_length=100, default="9999999999")