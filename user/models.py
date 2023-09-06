from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    photo =models.ImageField(upload_to="user_profile_photos/", blank=True)
    bio = models.TextField(max_length=1000, blank=True)
    interests = models.ManyToManyField('main.Interest', blank=True)
    location = models.CharField(max_length=256, blank=True)
    location_lat = models.FloatField(null=True, blank=True)
    location_lng = models.FloatField(null=True, blank=True)
    def __str__(self) -> str:
        return self.username