from django.shortcuts import render
from django.http import HttpResponse
from formtools.wizard.views import SessionWizardView
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

def group(request):
    return HttpResponse("Hello, group!")

class FormWizardView(LoginRequiredMixin, SessionWizardView):
    login_url = '/user/login'  # Set custom login URL
    redirect_field_name = 'next'  # Set custom redirect field name
    raise_exception = False  # Raise an exception instead of redirecting (optional)

    template_name = "group/wizard.html"
    form_list = [LocationForm1, InterestsForm2, NameForm3, DescriptionForm4]

    def done(self, form_list, form_dict, **kwargs):
        instance = Group(
            location=form_dict['0'].cleaned_data['location'],
            name=form_dict['2'].cleaned_data['name'],
            description=form_dict['3'].cleaned_data['description'],
            creator=self.request.user
        )
        instance.save()

        for interest in form_dict['1'].cleaned_data['interests']:
            instance.interests.add(interest) 

        return render(self.request, 'group/profile.html', {
            'form_data': [form.cleaned_data for form in form_list],
        })