from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from main.models import JoinMode


# Create your models here.
class EventVisibility(models.TextChoices):
    PUBLIC = 'Public'
    MEMBERS_ONLY = 'Memebers Only'

class Status(models.TextChoices):
    CANCELED = 'Canceled'
    ACTIVE = 'Active'

class Event(models.Model):
    cover_photo = models.ImageField(upload_to="event_cover_photos/", blank=True)
    name = models.CharField(max_length=64)
    description = models.TextField(max_length=500)
    visibility = models.CharField(max_length=20, choices=EventVisibility.choices, default=EventVisibility.PUBLIC)
    join_mode = models.CharField(max_length=10, choices=JoinMode.choices, default=JoinMode.DIRECT)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(1000)])
    location = models.CharField(max_length=64)
    location_lat = models.FloatField(null=True, blank=True)
    location_lng = models.FloatField(null=True, blank=True)
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')

    hosts = models.ManyToManyField('user.User', related_name='hosting_events')
    attendees = models.ManyToManyField('user.User', blank=True, related_name="attending_events")
    interests = models.ManyToManyField('main.Interest', blank=True, related_name="events")
    photos = models.ManyToManyField('main.Photo', blank=True, related_name="event")

    def __str__(self) -> str:
        return self.name

class GroupEvent(Event):
    group = models.ForeignKey('group.Group', on_delete=models.CASCADE, related_name='events')

class EventRequest(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='requests')
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='event_requests')
    created_at = models.DateTimeField(auto_now_add=True)
