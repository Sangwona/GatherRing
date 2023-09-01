from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import User

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']

class EditUserForm(forms.ModelForm):
    new_password1 = forms.CharField(label="New Password", widget=forms.PasswordInput, required=False)
    new_password2 = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput, required=False)
    location = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True, 'id': 'api-location'}))
    location_lat = forms.FloatField(required=False, widget=forms.HiddenInput(attrs={'id': 'location-lat'}))
    location_lng = forms.FloatField(required=False, widget=forms.HiddenInput(attrs={'id': 'location-lng'}))
    class Meta:
        model = User
        fields = ['photo', 'bio', 'interests', 'location', 'location_lat', 'location_lng']
        
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password1 != new_password2:
            raise forms.ValidationError("New passwords do not match.")

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get("new_password1")

        if new_password:
            user.set_password(new_password)

        if commit:
            user.save()

        return user