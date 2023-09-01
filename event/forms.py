from django import forms
from .models import Event, GroupEvent

class CreateEventForm(forms.ModelForm):            
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    class Meta:
        model = Event
        exclude = ['cover_photo', 'status', 'created_at', 'creator', 'hosts', 'attendees', 'photos']
        widgets = {
            'location': forms.TextInput(attrs={'id': 'api-location', 'type':'text', 'class':'form-control', 'placeholder':'Location'}),
            'location_lat' : forms.HiddenInput(attrs={'id': 'location-lat'}),
            'location_lng' : forms.HiddenInput(attrs={'id': 'location-lng'}),
        }

class CreateGroupEventForm(CreateEventForm):            
    class Meta:
        model = GroupEvent
        exclude = ['cover_photo', 'status', 'location_lat', 'location_lng', 'created_at', 'creator', 'attendees', 'photos', 'group', 'hosts']

class EditEventForm(forms.ModelForm):            
    class Meta:
        model = Event
        exclude = ['created_at', 'creator', 'attendees', 'photos']
        widgets = {
            'name': forms.TextInput(attrs={'type':'text', 'class':'form-control', 'placeholder':'Title'}),
            'description': forms.Textarea(attrs={'rows':'5', 'class':'form-control', 'placeholder':'Describe the event ...'}),
            'location': forms.TextInput(attrs={'id': 'api-location', 'type':'text', 'class':'form-control', 'placeholder':'Location'}),
            'location_lat' : forms.HiddenInput(attrs={'id': 'location-lat'}),
            'location_lng' : forms.HiddenInput(attrs={'id': 'location-lng'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class':'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class':'form-control'}),
            'cover_photo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'max_members': forms.NumberInput(attrs={'class': 'form-control'}),
            'visibility': forms.Select(attrs={'class':'form-control'}),
            'join_mode': forms.Select(attrs={'class':'form-control'}),
            'status': forms.Select(attrs={'class':'form-control'}),
            'hosts': forms.SelectMultiple(attrs={'class':'form-control'}),
            'categories': forms.SelectMultiple(attrs={'class':'form-control'}),
        }

class EditGroupEventForm(EditEventForm):            
    class Meta:
        model = GroupEvent
        exclude = ['created_at', 'creator', 'attendees', 'photos', 'group']