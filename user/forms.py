from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import User

class RegisterForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Confirm Password'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'type':'text', 'class':'form-control', 'placeholder':'Username'}))
    
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.TextInput(attrs={'autofocus': True, 'type':'text', 'class':'form-control', 'placeholder':'Email'})
        }

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True, 'type':'text', 'class':'form-control', 'placeholder':'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}))

class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['photo', 'bio', 'interests', 'location', 'location_lat', 'location_lng']
        widgets = {
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'bio': forms.Textarea(attrs={'rows':'4', 'class':'form-control', 'placeholder':'A few words about you ...'}),
            'interests': forms.SelectMultiple(attrs={'class':'form-control'}),
            'location': forms.TextInput(attrs={'id': 'api-location', 'type':'text', 'class':'form-control', 'placeholder':'Location'}),
            'location_lat' : forms.HiddenInput(attrs={'id': 'location-lat'}),
            'location_lng' : forms.HiddenInput(attrs={'id': 'location-lng'}),
        }
        
    # def clean(self):
    #     cleaned_data = super().clean()
    #     new_password1 = cleaned_data.get("new_password1")
    #     new_password2 = cleaned_data.get("new_password2")

    #     if new_password1 and new_password1 != new_password2:
    #         raise forms.ValidationError("New passwords do not match.")

    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     new_password = self.cleaned_data.get("new_password1")

    #     if new_password:
    #         user.set_password(new_password)

    #     if commit:
    #         user.save()

    #     return user