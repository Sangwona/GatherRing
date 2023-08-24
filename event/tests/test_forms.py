from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from event.models import EventVisibility, Status, GroupEvent
from event.forms import CreateEventForm, CreateGroupEventForm
from main.models import JoinMode
from group.models import Group

class CreateEventFormTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.creator = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

        self.group = Group.objects.create(
            location='Sample Location',
            name='Sample Group',
            description='Sample Description',
            creator=self.creator
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

    def test_create_group_event_form_valid_data(self):
        form = CreateGroupEventForm(data=self.form_data)
        self.assertTrue(form.is_valid())
        event = form.save(commit=False)
        event.creator = self.creator
        event.group = self.group
        event.save()
        self.assertEqual(GroupEvent.objects.count(), 1)

    def test_create_group_event_form_missing_required_fields(self):
        form = CreateGroupEventForm(data={})  # Empty data
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("description", form.errors)
        self.assertIn("capacity", form.errors)

    def test_create_event_form_invalid_data(self):
        form = CreateGroupEventForm(data={})
        self.assertFalse(form.is_valid())