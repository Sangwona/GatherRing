from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import CreateEventForm, CreateGroupEventForm
from django.contrib.auth.decorators import login_required
from group.models import Group

# Create your views here.

def event(request):
    return HttpResponse("Hello, event!")

def create(request):
    if request.method == "POST":
        createEventForm = CreateEventForm(request.POST)
        if createEventForm.is_valid():
            event = createEventForm.save(commit=False)
            event.creator = request.user
            event.save()

            return render(request, "event/profile.html", {
                'form_data': createEventForm.cleaned_data
            })
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
            gruop_event = createGroupEventForm.save(commit=False)
            gruop_event.creator = request.user
            gruop_event.group = Group.objects.get(pk=group_id)
            gruop_event.save()

            return render(request, "event/profile.html", {
                'form_data': createGroupEventForm.cleaned_data
            })

        else:
            return render(request, "event/create_ingroup.html", {
                'form': createGroupEventForm
            })        

    else:
        return render(request, "event/create_ingroup.html", {
            'form': CreateGroupEventForm(),
            'group_id' : group_id
        }) 