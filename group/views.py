from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

from formtools.wizard.views import SessionWizardView
from django.core.exceptions import PermissionDenied

from .forms import *
from .models import GroupRequest

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
    if request.user in group.admins.all():
        return render(request, "group/manage.html", {
            'requests': group.requests.all()
        })
    else:
        raise PermissionDenied

def all(request):
    return render(request, "group/all.html", {
        'groups': Group.objects.all(),
    })

@login_required
def toggle_membership(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if (request.user in group.members.all()):
        group.members.remove(request.user)
        joined = False
    else:
        group.members.add(request.user)
        joined = True
    
    data = {
        'joined': joined,
        'member_count': group.members.count()
    }

    return JsonResponse(data)

@login_required
def toggle_request(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    user = request.user

    existing_request = group.requests.filter(user=user).first()

    if existing_request:
        existing_request.delete()
        requested = False
    else:
        r = GroupRequest()
        r.user = user
        r.group = group
        r.save()
        requested = True

    return JsonResponse({"requested": requested}, status=201)

def show_group_members(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    members = group.members.all().values('id', 'username')
    return JsonResponse(list(members), safe=False)