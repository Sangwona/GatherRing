from django.shortcuts import render, redirect
from formtools.wizard.views import SessionWizardView
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

def profile(request, group_id):
    group = Group.objects.get(pk=group_id)
    return render(request, "group/profile.html", {
        'group': group,
        'request_exists': group.requests.filter(user=request.user).exists()
    })

class CreateGroupFormWizard(LoginRequiredMixin, SessionWizardView):
    login_url = '/user/login'  # Set custom login URL
    template_name = "group/create.html"
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

        return redirect('group_profile', instance.id)

def all(request):
    return render(request, "group/all.html", {
        'groups': Group.objects.all(),
    })