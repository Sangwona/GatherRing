from django import forms
from .models import Photo, Interest

class AddPhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['photo']
        widgets = {
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control-file'})
        }

class SearchFilterForm(forms.Form):
    SEARCH_CHOICES = (
        ('group', 'Group'),
        ('event', 'Event'),
    )

    search_type = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        initial='event',  # Set the default choice if desired
    )
    
    search_query = forms.CharField(
        label='Search Query',
        required=False,  # Make it optional
        max_length=100,  # Adjust the max length as needed
    )
    
    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    
    # distance = forms.DecimalField(
    #     label='Distance (optional)',
    #     required=False,
    # )
    
    start_time = forms.DateTimeField(
        label='Start Time (optional)',
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d'],
    )
    
    end_time = forms.DateTimeField(
        label='End Time (optional)',
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d'],
    )

    