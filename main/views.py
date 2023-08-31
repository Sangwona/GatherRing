from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone

from group.models import Group, GroupVisibility
from event.models import Event, Status, EventVisibility

def index(request):
    # when they are not logged in. = landing page

    # when they are logged in. = customized landing page

    return render(request, "main/index.html", {
        "list": Event.objects.all() # this should change to after we set what we are going to show for user's
    })

def search(request):
   
    query_terms = request.GET["q"].split()
    
    combined = list(searchGroup(query_terms)) + list(searchEvent(query_terms))
    return render(request, "main/index.html", {
        "list": combined
        })

def searchGroup(query_terms):

    query = Q()
    for term in query_terms:
        query |= Q(name__icontains=term) | Q(description__icontains=term)

    return Group.objects.filter(query)

def searchEvent(query_terms):

    query = Q()
    for term in query_terms:
        query |= Q(name__icontains=term) | Q(description__icontains=term)

    current_time = timezone.now()
    return Event.objects.filter(query).filter(
        status = Status.ACTIVE,
        start_time__gt = current_time,
        visibility = EventVisibility.PUBLIC
    )