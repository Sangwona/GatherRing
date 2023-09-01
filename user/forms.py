from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import User

class RegisterForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Confirm Password'}))

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'type':'text', 'class':'form-control', 'placeholder':'Username'})
        }

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}))
    class Meta:
        model = User
        fields = ['username', 'password']

class EditUserForm(forms.ModelForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}), required=False)
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}), required=False)

    class Meta:
        model = User
        fields = ['photo', 'bio', 'interests', 'location']
        widgets = {
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'bio': forms.Textarea(attrs={'rows':'4', 'class':'form-control', 'placeholder':'A few words about you ...'}),
            'interests': forms.SelectMultiple(attrs={'class':'form-control'}),
            'location': forms.TextInput(attrs={'id': 'location-name', 'type':'text', 'class':'form-control', 'placeholder':'Location'}),
        }
        
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