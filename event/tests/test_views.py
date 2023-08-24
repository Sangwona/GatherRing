from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.test import RequestFactory
from django.core.exceptions import ObjectDoesNotExist  # Import the exception

from event.models import Event, EventVisibility, Status
from event.views import create_ingroup
from group.models import Group
from main.models import JoinMode

class BaseViewTest(TestCase):
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

class EventViewsTest(BaseViewTest):
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

class GroupEventViewsTest(BaseViewTest):
    def setUp(self):
        super().setUp()  # Call the parent setup to set up common data
        self.group = Group.objects.create(
            location='Sample Location',
            name='Sample Group',
            description='Sample Description',
            creator=self.user
        )
        
        self.group_event_form_data = {
            'name': 'Test Group Event',
            'description': 'This is a test group event.',
            'visibility': EventVisibility.PUBLIC,
            'join_mode': JoinMode.DIRECT,
            'status': Status.ACTIVE,
            'capacity': 10,
            'location': 'Test Location',
            'start_time': timezone.now(),
            'end_time': timezone.now() + timezone.timedelta(hours=2),
            'group': self.group
        }

    def test_create_group_event_view_GET(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('create_event_ingroup', args=[str(self.group.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create GroupEvent')

    def test_create_group_event_view_POST_valid_form(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('create_event_ingroup', args=[str(self.group.id)]), data=self.group_event_form_data)
        self.assertEqual(response.status_code, 200)  # Assuming you're rendering a template

    def test_create_group_event_view_POST_group_not_found(self):
        self.client.login(username='testuser', password='testpassword')
        non_existent_group_id = 9999  # An ID that does not exist in your database
        with self.assertRaises(ObjectDoesNotExist):  # Catch the exception
            self.client.post(reverse('create_event_ingroup', args=[str(non_existent_group_id)]), data=self.group_event_form_data)
