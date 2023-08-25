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
            group_event = createGroupEventForm.save(commit=False)
            group_event.creator = request.user
            group_event.group = Group.objects.get(pk=group_id)
            group_event.save()

            return render(request, "event/profile.html", {
                'form_data': createGroupEventForm.cleaned_data
            })

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