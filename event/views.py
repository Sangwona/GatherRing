from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse

from .forms import CreateEventForm, CreateGroupEventForm, EditEventForm
from .models import Event, EventRequest

from group.models import Group


# Create your views here.
def create(request):
    if request.method == "POST":
        createEventForm = CreateEventForm(request.POST)
        if createEventForm.is_valid():
            event = createEventForm.save(commit=False)
            event.creator = request.user
            event.save()
            return event_profile(request, event.id)
        else:
            return render(request, "event/create.html", {
                'form': createEventForm
            })
    else:
        return render(request, "event/create.html", {
            'form': CreateEventForm(),
        }) 
    
@login_required
def create_ingroup(request, group_id):
    if request.method == "POST":
        createGroupEventForm = CreateGroupEventForm(request.POST)
        if createGroupEventForm.is_valid():
            group_event = createGroupEventForm.save(commit=False)
            group_event.creator = request.user
            group_event.group = Group.objects.get(pk=group_id)
            group_event.save()

            return event_profile(request, group_event.id)

        else:
            return render(request, "event/create_ingroup.html", {
                'form': createGroupEventForm,
                'group_id' : group_id
            })        

    else:
        return render(request, "event/create_ingroup.html", {
            'form': CreateGroupEventForm(),
            'group_id' : group_id
        }) 
    
def edit(request, event_id):
    event = Event.objects.get(pk=event_id)

    if request.method == "POST":
        form = EditEventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return event_profile(request, event_id)
    else:
        form = EditEventForm(instance=event)
    return render(request, "event/edit.html", {
        "form": form,
        "event_id": event_id
    })
    
def event_profile(request, event_id):
    event = Event.objects.get(pk=event_id)

    if request.user.is_authenticated:
        request_exists = event.requests.filter(user=request.user.id).exists()
    else:
        request_exists = False

    return render(request, "event/profile.html", {
        "event" : event,
        "request_exists" : request_exists
    })

def all(request):
    event = Event.objects.all().order_by("-created_at")
    paginator = Paginator(event, 10) # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "event/all.html", {
        'events': page_obj,
        'is_paginated': page_obj.has_other_pages(),
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
    if (request.user in event.attendees.all()):
        event.attendees.remove(request.user)
        joined = False
    else:
        event.attendees.add(request.user)
        joined = True
    
    data = {
        'joined': joined,
        'attendee_count': event.attendees.count()
    }

    return JsonResponse(data)

@login_required
def toggle_request(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    user = request.user

    existing_request = event.requests.filter(user=user).first()

    if existing_request:
        existing_request.delete()
        requested = False
    else:
        eventRequest = EventRequest()
        eventRequest.user = user
        eventRequest.event = event
        eventRequest.save()
        requested = True

    return JsonResponse({"requested": requested}, status=201)