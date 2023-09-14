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
from geopy.distance import geodesic

def index(request):
    # when they are not logged in. = landing page

    # when they are logged in. = customized landing page

    return render(request, "main/index.html", {
        "list": Event.objects.all() # this should change to after we set what we are going to show for user's
    })


def search(request):
    data = json.loads(request.body)

    query_terms = data['query'].split()
    search_type = data['search_type']
    previous_query_terms = request.session['query_terms'] if 'query_terms' in request.session else []; 
    
    if not query_terms:
        dataset = Group.objects.all() if search_type == 'Group' else Event.objects.all()
    elif query_terms != previous_query_terms:
        query = Q()
        for term in query_terms:
            query |= Q(name__icontains=term) | Q(description__icontains=term)
        
        groups = Group.objects.filter(query)
        events = Event.objects.filter(query).filter(
            status = Status.ACTIVE,
            visibility = EventVisibility.PUBLIC,
            # start_time__gt = timezone.now(),
            )

        request.session['query_terms'] = query_terms
        request.session['group_ids'] = list(groups.values_list('id', flat=True)) 
        request.session['event_ids'] = list(events.values_list('id', flat=True))

        dataset = groups if search_type == 'Group' else events
    else:
        dataset = Group.objects.filter(id__in=request.session['group_ids']) if search_type == 'Group' else Event.objects.filter(id__in=request.session['event_ids'])

    if search_type == 'Event':
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
    
    category = data['category']
    if category != 'any':
        dataset = dataset.filter(interests__in=category)
    
    distance = data['distance']
    if distance != 'any':
        user_location = (data['lat'], data['lng'])
        max_distance = int(distance)
        filter_conditions = Q()

        for event in dataset:
            event_location = (event.location_lat, event.location_lng)
            print("event location: " + str(event_location))
            event_distance = geodesic(user_location, event_location).kilometers
            print(event_distance)
            if event_distance <= max_distance:
                filter_conditions |= Q(id=event.id)  

        dataset = dataset.filter(filter_conditions)

    events_html = render_to_string('main/search_result.html', {'list': dataset}, request=request)
    return JsonResponse({'html': events_html, 'count': dataset.count()})
