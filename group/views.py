from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from formtools.wizard.views import SessionWizardView

from .forms import *

# Create your views here.

def profile(request, group_id):
    group = Group.objects.get(pk=group_id)
    if request.user.is_authenticated:
        request_exists = group.requests.filter(user=request.user).exists()
    else:
        request_exists = False

    return render(request, "group/profile.html", {
        'group': group,
        'request_exists': request_exists
    })

class CreateGroupFormWizard(LoginRequiredMixin, SessionWizardView):
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

@login_required
def edit(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    
    if (request.method == "POST"):
        editGroupForm = EditGroupForm(request.POST, request.FILES, instance=group)
        if editGroupForm.is_valid():
            editGroupForm.save()
            return redirect("group_profile", group_id=group_id)
        
    else:
        editGroupForm = EditGroupForm(instance=group)
    
    return render(request, "group/edit.html", {
        "form": editGroupForm,
        "group_id": group_id
    })

@login_required
def manage(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    return render(request, "group/manage.html", {
        'requests': group.requests.all()
    })

def all(request):
    return render(request, "group/all.html", {
        'groups': Group.objects.all(),
    })