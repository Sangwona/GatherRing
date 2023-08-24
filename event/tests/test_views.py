from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from event.models import Event, EventVisibility, Status
from main.models import JoinMode

class EventViewsTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        self.form_data = {
            'name': 'Test Event',
            'description': 'This is a test event',
            'visibility': EventVisibility.PUBLIC,
            'join_mode': JoinMode.DIRECT,
            'status': Status.ACTIVE,
            'capacity': 50,
            'location': 'Test Location',
            'start_time': timezone.now(),
            'end_time': timezone.now() + timezone.timedelta(hours=2),
        }

    def test_create_event_view_GET(self):
        # Test the create event view with a GET request
        response = self.client.get(reverse('create_event'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/create.html')

    def test_create_event_view_valid_POST(self):
        # Test the create event view with a valid POST request
        self.client.login(username='testuser', password='testpassword')  # Log in the user
        response = self.client.post(reverse('create_event'), data=self.form_data)

        self.assertEqual(response.status_code, 200)  # Successful form submission should return a 200
        self.assertTemplateUsed(response, 'event/profile.html')

        # Check if the event was created and associated with the user
        event = Event.objects.first()
        self.assertIsNotNone(event)
        self.assertEqual(event.name, 'Test Event')
        self.assertEqual(event.creator, self.user)

    def test_create_event_view_invalid_POST(self):
        # Test the create event view with an invalid POST request (missing required fields)
        invalid_data = self.form_data.copy()
        invalid_data.pop("name")

        self.client.login(username='testuser', password='testpassword')  # Log in the user
        response = self.client.post(reverse('create_event'), data=invalid_data)

        self.assertEqual(response.status_code, 200)  # Form submission should return a 200
        self.assertTemplateUsed(response, 'event/create.html')

        # Check if the form has errors
        self.assertFormError(response, 'form', 'name', 'This field is required.')
