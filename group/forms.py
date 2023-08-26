from django import forms
from .models import Group
from main.models import Interest

class LocationForm1(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["location"]

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
    class Meta:
        model = Group
        exclude = ["creator", "photos", "members", "created_at"]
    
    def __init__(self, *args, **kwargs):
        group = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        if group:
            self.fields['admins'].queryset = group.members.all()