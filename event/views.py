import json
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse

from .forms import CreateEventForm, EditEventForm
from .models import Event, GroupEvent, EventRequest, Status
from group.models import Group
from main.models import Photo
from main.forms import AddPhotoForm

# Create your views here.
@login_required
def create(request, group_id=None):
    group = get_object_or_404(Group, pk=group_id) if group_id else None
    if group and request.user not in group.admins.all():
        raise PermissionDenied
    initial_data = {}
    if group:
        initial_data['groups'] = [group]

    form = CreateEventForm(initial=initial_data, user=request.user)
        
    if request.method == "POST":
        form = CreateEventForm(request.POST, user=request.user)
        if form.is_valid():
            if 'groups' in form.cleaned_data and form.cleaned_data['groups']:
                for group in form.cleaned_data.get('groups'):
                    groupEvent = GroupEvent.objects.create(
                        name=form.cleaned_data['name'],
                        description=form.cleaned_data['description'],
                        visibility=form.cleaned_data['visibility'],
                        join_mode=form.cleaned_data['join_mode'],
                        capacity=form.cleaned_data['capacity'],
                        location=form.cleaned_data['location'],
                        location_lat=form.cleaned_data['location_lat'],
                        location_lng=form.cleaned_data['location_lng'],
                        start_time=form.cleaned_data['start_time'],
                        end_time=form.cleaned_data['end_time'],
                        creator=request.user,
                        group=group,
                    )
                return event_profile(request, groupEvent.id)
            else:
                event = form.save(commit=False)
                event.creator = request.user
                event.save()
                return event_profile(request, event.id)
        else: 
            print(form.errors)
            
    return render(request, "event/create.html", {
        'form': form,
        'group': group
    })            
    
@login_required
def edit(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.user not in event.hosts.all():
        raise PermissionDenied

    if request.method == "POST":
        form = EditEventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return event_profile(request, event_id)
        else:
            print(form.errors)
    else:
        form = EditEventForm(instance=event)

    return render(request, "event/edit.html", {
        "form": form,
        "event_id": event_id,
        "photo_url": event.cover_photo.url if event.cover_photo else None
    })
    
def event_profile(request, event_id):
    event = Event.objects.get(pk=event_id)

    if request.user.is_authenticated:
        request_exists = event.requests.filter(user=request.user.id).exists()
    else:
        request_exists = False

    return render(request, "event/profile.html", {
        "event" : event,
        "request_exists" : request_exists,
        "form": AddPhotoForm()
    })

def all(request):
    events = Event.objects.all().order_by("-created_at")

    return render(request, "event/all.html", {
        'events': events
    })

@login_required
def manage_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.user in event.hosts.all():
        return render(request, "event/manage.html", {
            'requests': event.requests.all()
        })
    else:
        raise PermissionDenied
    
@login_required
def toggle_attendance(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    updated_data = {"event_id": event_id,
                    "user_id": request.user.id
                    }
    if (request.user in event.attendees.all()):
        event.attendees.remove(request.user)
        updated_data["message"] = "Successfully removed attendee"
    else:
        event.attendees.add(request.user)
        updated_data["message"] = "Successfully removed attendee"
    
    return JsonResponse(updated_data)

@login_required
def toggle_request(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    user = request.user

    existing_request = event.requests.filter(user=user).first()

    if existing_request:
        existing_request.delete()
        return JsonResponse({"requested": False}, status=204)
    else:
        eventRequest = EventRequest()
        eventRequest.user = user
        eventRequest.event = event
        eventRequest.save()
        return JsonResponse({"requested": True}, status=201)



def show_event_attendees(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    attendees = event.attendees.all().values('id', 'username')
    return JsonResponse(list(attendees), safe=False)

@login_required
def handle_request(request, request_id):
    eventRequest = get_object_or_404(EventRequest, pk=request_id)
    requestedEvent = eventRequest.event
    requestedUser = eventRequest.user

    if request.user in requestedEvent.hosts.all():
        data = json.loads(request.body)
        if data.get("action") == "accept":
            requestedEvent.attendees.add(requestedUser)
        eventRequest.delete()
        return JsonResponse({"message": "success"}, status=201)      
    else:
        raise PermissionDenied
    
@login_required
def change_status_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    data = json.loads(request.body)
    if request.user in event.hosts.all():
        if data.get("action", "") == "reactive":
            event.status = Status.ACTIVE        
        else:
            event.status = Status.CANCELED
        event.save()

    return JsonResponse({"message": "success"}, status=201)   

@login_required
def add_photo(request, event_id):
    if request.method == 'POST':
        event = Event.objects.get(pk=event_id)
        if request.user in event.attendees.all():
            photo = Photo.objects.create(photo=request.FILES['photo'], uploaded_by=request.user)
            photo.related_event = event
            photo.save()
            event.photos.add(photo)
            return redirect("event_profile", event_id)
        else:
            raise PermissionDenied
        
def is_attendee(request, event_id):
    event = Event.objects.get(pk=event_id)
    is_attendee = False
    if request.user in event.attendees.all():
        is_attendee = True
    
    return JsonResponse({"is_attendee": is_attendee})

def get_photos(request, event_id):
    event = Event.objects.get(pk=event_id)
    data = {
        'photos': [photo.photo.url for photo in event.photos.all()]
    }
    return JsonResponse(data)

@login_required
def delete(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.user == event.creator:
        if request.method == 'POST':
            event.delete()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'failure'})
    else:
        raise PermissionDenied
