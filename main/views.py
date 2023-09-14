import json 
import datetime
import pytz

from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone
from group.models import Group
from event.models import Event, Status, EventVisibility
from django.template.loader import render_to_string
from django.http import JsonResponse

def index(request):
    # when they are not logged in. = landing page

    # when they are logged in. = customized landing page

    return render(request, "main/index.html", {
        "list": Event.objects.all() # this should change to after we set what we are going to show for user's
    })

def search(request):
    query_terms = request.GET["q"].split()

    if 'query_terms' in request.session and request.session['query_terms'] == query_terms:
        groups = Group.objects.filter(id__in=request.session['group_ids'])
        events = Event.objects.filter(id__in=request.session['event_ids'])
    else:
        query = Q()
        for term in query_terms:
            query |= Q(name__icontains=term) | Q(description__icontains=term)
        
        groups = Group.objects.filter(query)
        events = Event.objects.filter(query).filter(
            status = Status.ACTIVE,
            start_time__gt = timezone.now(),
            visibility = EventVisibility.PUBLIC
            )

        request.session['query_terms'] = query_terms
        request.session['group_ids'] = list(groups.values_list('id', flat=True)) 
        request.session['event_ids'] = list(events.values_list('id', flat=True)) 

    return render(request, "main/index.html", {
        "list": list(events) + list(groups)
        })

def filter(request):
    data = json.loads(request.body)
    if data['search_type'] == "Group":
        if 'query_terms' in request.session:
            dataset = Group.objects.filter(id__in=request.session['group_ids'])
        else: 
            dataset = Group.objects.all()
    else:
        if 'query_terms' in request.session:
            dataset = Event.objects.filter(id__in=request.session['event_ids'])
        else: 
            dataset = Event.objects.all()

        date = data['date']
        if date != 'any':  
            user_timezone = pytz.timezone(data['userTimezone'])
            today = timezone.now().astimezone(user_timezone)

            if date == 'today':
                start_time = datetime.datetime.combine(today, datetime.time.min)
                end_time = datetime.datetime.combine(today, datetime.time.max)
            elif date == 'tomorrow':
                tomorrow = today + datetime.timedelta(days=1)
                start_time = datetime.datetime.combine(tomorrow, datetime.time.min)
                end_time = datetime.datetime.combine(tomorrow, datetime.time.max)
            elif date == 'week':
                start_time = today - datetime.timedelta(days=today.weekday())  # Start of the current week
                end_time = start_time + datetime.timedelta(days=6)  # End of the current week
            else: #weekend
                saturday = today + datetime.timedelta(days=(5 - today.weekday()) % 7)  # Find the nearest Saturday
                start_time = datetime.datetime.combine(saturday, datetime.time.min)
                end_time = datetime.datetime.combine(saturday + datetime.timedelta(days=1), datetime.time.max)
                        
            dataset = dataset.filter(start_time__gte=start_time)
            dataset = dataset.filter(start_time__lte=end_time)    
    
    # distance = data['distance']
    # if distance != 'any':
    #     max_distance = int(distance)
    #     start_location = data['location']
    #     #some filtering by distance

    category = data['category']
    if category != 'any':
        dataset = dataset.filter(interests__in=category)

    events_html = render_to_string('main/search_result.html', {'list': dataset}, request=request)
    return JsonResponse({'html': events_html, 'count': dataset.count()})
