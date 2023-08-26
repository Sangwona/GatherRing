from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from event.models import EventVisibility, Status
from event.forms import CreateEventForm, CreateGroupEventForm, EditEventForm, EditGroupEventForm
from main.models import JoinMode

class BaseFormTest(TestCase):
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

class CreateEventFormTest(BaseFormTest):
    def test_create_event_form_valid(self):
        form = CreateEventForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_create_event_form_invalid(self):
        invalid_data = self.form_data.copy()
        invalid_data.pop("name")
        form = CreateEventForm(data=invalid_data)
        self.assertFalse(form.is_valid())

class CreateGroupEventFormTest(BaseFormTest):
    def test_create_group_event_form_valid_data(self):
        form = CreateGroupEventForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_create_group_event_form_missing_required_fields(self):
        form = CreateGroupEventForm(data={})  # Empty data
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("description", form.errors)
        self.assertIn("capacity", form.errors)
    
class EditEventFormTest(BaseFormTest):
    def test_valid_edit_event_form(self):
        valid_form_data = self.form_data.copy()
        valid_form_data['hosts'] = [self.creator.pk]
        form = EditEventForm(data=valid_form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_edit_event_form(self):
        invalid_data = self.form_data.copy() # missing hosts
        form = EditEventForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("hosts", form.errors)

class EditGroupEventFormTest(BaseFormTest):
    def test_valid_edit_group_event_form(self):
        valid_form_data = self.form_data.copy()
        valid_form_data['hosts'] = [self.creator.pk]
        form = EditGroupEventForm(data=valid_form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_edit_group_event_form(self):
        invalid_data = self.form_data.copy() # missing hosts
        form = EditGroupEventForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("hosts", form.errors)