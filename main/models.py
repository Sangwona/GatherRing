from django.db import models

# Create your models here.
class JoinMode(models.TextChoices):
    DIRECT = 'Direct'
    REQUEST = 'Request'
    INVITE = 'Invite'

class Interest(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self) -> str:
        return self.name

class Photo(models.Model):
    uploaded_by = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True, blank= True)
    photo = models.ImageField(upload_to="photos/")
    uploaded_at = models.DateField(auto_now_add=True)
    related_event = models.ForeignKey('event.Event', on_delete=models.CASCADE, null=True, blank=True, related_name='event_photo')
    related_group_event = models.ForeignKey('event.GroupEvent', on_delete=models.SET_NULL, null=True, blank=True, related_name='group_event_photo')
    related_group = models.ForeignKey('group.Group', on_delete=models.CASCADE, null=True, blank=True, related_name='group_photo')

    def __str__(self) -> str:
        return self.photo.name