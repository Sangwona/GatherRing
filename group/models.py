from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from main.models import JoinMode

# Create your models here.
class GroupVisibility(models.TextChoices):
    PUBLIC = 'Public'
    PRIVATE = 'Private'

class Group(models.Model):  
    name = models.CharField(max_length=64)
    visibility = models.CharField(max_length=16, choices=GroupVisibility.choices, default=GroupVisibility.PUBLIC)
    location = models.CharField(max_length=64)
    description = models.TextField(max_length=500)
    join_mode = models.CharField(max_length=10, choices=JoinMode.choices, default=JoinMode.DIRECT)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(1000)], default=50)
    admins = models.ManyToManyField('user.User', related_name="administrating_groups")
    members = models.ManyToManyField('user.User', blank=True, related_name="attending_groups")
    creator = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='created_groups')
    
    created_at = models.DateTimeField(auto_now_add=True)
    interests = models.ManyToManyField('main.Interest', blank=True, related_name="groups")
    photos = models.ManyToManyField('main.Photo', blank=True, related_name="groups")
    cover_photo = models.ImageField(upload_to="group_cover_photos/", blank=True)

    def __str__(self) -> str:
        return self.name
    
    def save(self, *args, **kwargs):
        is_new = not bool(self.pk)  # check if the object is newly created
        super().save(*args, **kwargs)  # save the instance to get its id

        if is_new:
        # add the creator as an admins/members
            self.admins.add(self.creator)
            self.members.add(self.creator)
        
class GroupRequest(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='requests')
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='group_requests')
    created_at = models.DateTimeField(auto_now_add=True)