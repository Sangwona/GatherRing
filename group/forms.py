from django import forms
from .models import Group
from main.models import Interest

class LocationForm1(forms.ModelForm):
    location = forms.CharField(
        widget=forms.TextInput(attrs={'autofocus': True, 'id': 'api-location'})
    )
    location_lat = forms.FloatField(required=False, widget=forms.HiddenInput(attrs={'id': 'location-lat'}))
    location_lng = forms.FloatField(required=False, widget=forms.HiddenInput(attrs={'id': 'location-lng'}))
    class Meta:
        model = Group
        fields = ["location", "location_lat", "location_lng"]

class InterestsForm2(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["interests"]

class NameForm3(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name"]

class DescriptionForm4(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["description"]

class EditGroupForm(forms.ModelForm):
    location = forms.CharField(
        widget=forms.TextInput(attrs={'autofocus': True, 'id': 'api-location'})
    )
    location_lat = forms.FloatField(required=False, widget=forms.HiddenInput(attrs={'id': 'location-lat'}))
    location_lng = forms.FloatField(required=False, widget=forms.HiddenInput(attrs={'id': 'location-lng'}))
    class Meta:
        model = Group
        exclude = ["creator", "photos", "members", "created_at"]
    
    def __init__(self, *args, **kwargs):
        group = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        if group:
            self.fields['admins'].queryset = group.members.all()