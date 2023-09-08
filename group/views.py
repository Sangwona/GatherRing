import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from formtools.wizard.views import SessionWizardView

from .forms import *
from .models import GroupRequest
from event.models import Status, EventVisibility
from main.models import Photo
from main.forms import AddPhotoForm

# Create your views here.

def profile(request, group_id):
    group = Group.objects.get(pk=group_id)

    request_exists = False
    if request.user.is_authenticated:
        request_exists = group.requests.filter(user=request.user).exists()

    if request.user in group.members.all():
        past_events = group.events.filter(start_time__lt = timezone.now())
        upcoming_events = group.events.filter(start_time__gt = timezone.now(), status = Status.ACTIVE)
    else:
        past_events = group.events.filter(start_time__lt = timezone.now(), visibility = EventVisibility.PUBLIC)
        upcoming_events = group.events.filter(start_time__gt = timezone.now(), status = Status.ACTIVE, visibility = EventVisibility.PUBLIC)

    return render(request, "group/profile.html", {
        'group': group,
        'request_exists': request_exists,
        "form": AddPhotoForm(),
        "past_events" : past_events, 
        "upcoming_events": upcoming_events,
        "first_four_members": group.members.all()[:4]
    })

class CreateGroupFormWizard(LoginRequiredMixin, SessionWizardView):
    template_name = "group/create.html"
    form_list = [LocationForm1, InterestsForm2, NameForm3, DescriptionForm4]

    def done(self, form_list, form_dict, **kwargs):
        
        instance = Group(
            location=form_dict['0'].cleaned_data['location'],
            location_lat = form_dict['0'].cleaned_data['location_lat'],
            location_lng = form_dict['0'].cleaned_data['location_lng'],
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
    if request.user not in group.admins.all():
        raise PermissionDenied
    
    if (request.method == "POST"):
        editGroupForm = EditGroupForm(request.POST, request.FILES, instance=group)
        if editGroupForm.is_valid():
            editGroupForm.save()
            return redirect("group_profile", group_id=group_id)
    else:
        editGroupForm = EditGroupForm(instance=group)
    
    return render(request, "group/edit.html", {
        "form": editGroupForm,
        "group_id": group_id,
        "photo_url": group.cover_photo.url if group.cover_photo else None
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

@login_required
def handle_request(request, request_id):
    groupRequest = get_object_or_404(GroupRequest, pk=request_id)
    requestedGroup = groupRequest.group
    requestedUser = groupRequest.user

    if request.user in requestedGroup.admins.all():
        data = json.loads(request.body)
        if data.get("action") == "accept":
            requestedGroup.members.add(requestedUser)
        groupRequest.delete()
        return JsonResponse({"message": "success"}, status=201)      
    else:
        raise PermissionDenied

@login_required
def delete(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if request.user == group.creator:
        if request.method == 'POST':
            group.delete()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'failure'})
    else:
        raise PermissionDenied

@login_required
def add_photo(request, group_id):
    if request.method == 'POST':
        group = get_object_or_404(Group, pk=group_id)
        if request.user in group.members.all():
            photo = Photo.objects.create(photo=request.FILES['photo'], uploaded_by=request.user)
            photo.related_group = group
            photo.save()
            group.photos.add(photo)
            return redirect("group_profile", group_id)
        else:
            raise PermissionDenied
        
def is_member(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    is_member = False
    if request.user in group.members.all():
        is_member = True
    
    return JsonResponse({"is_member": is_member})

def get_photos(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    data = {
        'photos': [photo.photo.url for photo in group.photos.all()]
    }
    return JsonResponse(data)