from django.db import models

from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='profile.jpg', upload_to='profile_pictures')
    contact_number = models.CharField(max_length=100, default="9999999999")
    
    def __str__(self):
        return self.user.username