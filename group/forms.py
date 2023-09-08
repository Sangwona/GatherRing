from django import forms
from .models import Group

class LocationForm1(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["location", "location_lat", "location_lng"]
        widgets = {
            'location': forms.TextInput(attrs={'id': 'api-location', 'type':'text', 'class':'form-control', 'placeholder':'Where is your group based?'}),
            'location_lat' : forms.HiddenInput(attrs={'id': 'location-lat'}),
            'location_lng' : forms.HiddenInput(attrs={'id': 'location-lng'})
        }

class InterestsForm2(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["interests"]
        labels  = {
        'interests':'Choose some topics related to your group', 
        }
        widgets = {
            'interests': forms.CheckboxSelectMultiple() 
        }

class NameForm3(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name"]
        widgets = {
            'name': forms.TextInput(attrs={'type':'text', 'class':'form-control', 'placeholder':'Give your group a name'})
        }

class DescriptionForm4(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["description"]
        widgets = {
            'description': forms.Textarea(attrs={'rows':'5', 'class':'form-control', 'placeholder':'Briefly describe your group ...'})
        }

class EditGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = ["creator", "photos", "members", "created_at"]
        widgets = {
            'cover_photo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'name': forms.TextInput(attrs={'type':'text', 'class':'form-control', 'placeholder':'Name'}),
            'description': forms.Textarea(attrs={'rows':'5', 'class':'form-control', 'placeholder':'Describe your group ...'}),
            'visibility': forms.RadioSelect(),
            'join_mode': forms.RadioSelect(),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'value': 50}),
            'location': forms.TextInput(attrs={'id': 'api-location', 'type':'text', 'class':'form-control', 'placeholder':'Location'}),
            'location_lat' : forms.HiddenInput(attrs={'id': 'location-lat'}),
            'location_lng' : forms.HiddenInput(attrs={'id': 'location-lng'}),
            'interests': forms.CheckboxSelectMultiple(),
            'admins': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        group = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        if group:
            self.fields['admins'].queryset = group.members.all()