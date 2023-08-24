from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from event.models import EventVisibility, Status
from main.models import JoinMode
from event.forms import CreateEventForm

class CreateEventFormTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.creator = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
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
    
    def test_create_event_form_valid(self):
        form = CreateEventForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_create_event_form_invalid(self):
        invalid_data = self.form_data.copy()
        invalid_data.pop("name")
        form = CreateEventForm(data=invalid_data)
        self.assertFalse(form.is_valid())