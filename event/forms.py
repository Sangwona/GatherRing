from django import forms
from .models import Event, GroupEvent

class CreateEventForm(forms.ModelForm):            
    class Meta:
        model = Event
        exclude = ['cover_photo', 'status', 'location_lat', 'location_lng', 'created_at', 'creator', 'hosts', 'attendees', 'photos']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class CreateGroupEventForm(forms.ModelForm):            
    class Meta:
        model = GroupEvent
        exclude = ['cover_photo', 'status', 'location_lat', 'location_lng', 'created_at', 'creator', 'attendees', 'photos', 'group', 'hosts']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }