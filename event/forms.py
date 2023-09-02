from django import forms
from .models import Event, GroupEvent

class CreateEventForm(forms.ModelForm):            
    class Meta:
        model = Event
        exclude = ['cover_photo', 'status', 'created_at', 'creator', 'hosts', 'attendees', 'photos']
        widgets = {
            'name': forms.TextInput(attrs={'type':'text', 'class':'form-control', 'placeholder':'Name'}),
            'description': forms.Textarea(attrs={'rows':'5', 'class':'form-control', 'placeholder':'Describe the event ...'}),
            'visibility': forms.RadioSelect(),
            'join_mode': forms.RadioSelect(),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'value': 50}),
            'location': forms.TextInput(attrs={'id': 'api-location', 'type':'text', 'class':'form-control', 'placeholder':'Location'}),
            'location_lat' : forms.HiddenInput(attrs={'id': 'location-lat'}),
            'location_lng' : forms.HiddenInput(attrs={'id': 'location-lng'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class':'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class':'form-control'}),
            'interests': forms.CheckboxSelectMultiple() 
        }

class CreateGroupEventForm(CreateEventForm):            
    class Meta:
        model = GroupEvent
        exclude = ['cover_photo', 'status', 'created_at', 'creator', 'hosts', 'attendees', 'photos', 'group']

class EditEventForm(forms.ModelForm):            
    class Meta:
        model = Event
        exclude = ['status', 'created_at', 'creator', 'attendees', 'photos']
        widgets = {
            'cover_photo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'name': forms.TextInput(attrs={'type':'text', 'class':'form-control', 'placeholder':'Name'}),
            'description': forms.Textarea(attrs={'rows':'5', 'class':'form-control', 'placeholder':'Describe the event ...'}),
            'visibility': forms.RadioSelect(),
            'join_mode': forms.RadioSelect(),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'id': 'api-location', 'type':'text', 'class':'form-control', 'placeholder':'Location'}),
            'location_lat' : forms.HiddenInput(attrs={'id': 'location-lat'}),
            'location_lng' : forms.HiddenInput(attrs={'id': 'location-lng'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class':'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class':'form-control'}),
            'hosts': forms.CheckboxSelectMultiple(),
            'interests': forms.CheckboxSelectMultiple()
        }

class EditGroupEventForm(EditEventForm):            
    class Meta:
        model = GroupEvent
        exclude = ['created_at', 'creator', 'attendees', 'photos', 'group']