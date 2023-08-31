from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from group.models import Group
from event.models import Event, EventVisibility
from main.models import JoinMode
from main.views import *

class IndexViewTest(TestCase):
    def test_index_view(self):
        # Make a GET request to the 'index' view
        response = self.client.get(reverse('index'))

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the response uses the 'main/index.html' template
        self.assertTemplateUsed(response, 'main/index.html')

class SearchTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.group = Group.objects.create(
            name="Test Group",
            description="This is a test group",
            location="Test Location",
            visibility="Public",
            join_mode="Direct",
            capacity=50,
            creator=self.user,
        )
        
        self.event = Event.objects.create(
            name='Test Event',
            description='This is a test event 1',
            visibility=EventVisibility.PUBLIC,
            join_mode=JoinMode.DIRECT,
            creator=self.user,
            capacity=50,
            location='Test Location',
            start_time=timezone.now() + timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=2)
        )

    def test_searchGroup(self):
        # Test searchGroup function
        group_results = searchGroup(["Test"])
        self.assertEqual(group_results.count(), 1)
        self.assertEqual(group_results[0].name, "Test Group")

    def test_searchEvent(self):
        # Test searchEvent function
        event_results = searchEvent(["Test"])
        self.assertEqual(event_results.count(), 1)
        self.assertEqual(event_results[0].name, "Test Event")
    
    def test_passedEvent(self):
        self.event = Event.objects.create(
            name='passed',
            description='This is a test event 1',
            visibility=EventVisibility.PUBLIC,
            join_mode=JoinMode.DIRECT,
            creator=self.user,
            capacity=50,
            location='Test Location',
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=2)
        )
        event_results = searchEvent(["passed"])
        self.assertEqual(event_results.count(), 0)

    def test_search(self):
        response = self.client.get(reverse("search"), {"q": "Test"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Group")
        self.assertContains(response, "Test Event")

    def test_no_results(self):
        # Mock a request to the search view with a nonexistent query
        response = self.client.get(reverse("search"), {"q": "Nonexistent"})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No results found.")