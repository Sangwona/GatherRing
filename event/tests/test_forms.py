from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from event.models import EventVisibility, Status
from event.forms import CreateEventForm, EditEventForm
from group.models import Group
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

    def test_create_event_form_missing_required_fields(self):
        form = CreateEventForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('description', form.errors)
        self.assertIn('join_mode', form.errors)
        self.assertIn('capacity', form.errors)
        self.assertIn('location', form.errors)
        self.assertIn('start_time', form.errors)
        self.assertIn('end_time', form.errors)
    
    def test_create_event_form_capacity_negative(self):
        data = self.form_data.copy()
        data['capacity'] = -10
        form = CreateEventForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('capacity', form.errors)

    # def test_create_event_form_end_time_before_start_time(self):
    #     data = self.form_data.copy()
    #     data['start_time'] = timezone.now()
    #     data['end_time'] = timezone.now() - timezone.timedelta(hours=2)
    #     form = CreateEventForm(data=data)
    #     self.assertFalse(form.is_valid())
    #     self.assertIn('end_time', form.errors)

    def test_create_event_form_with_user_groups(self):
        group = Group.objects.create(name='Test Group', creator=self.creator)
        form = CreateEventForm(data=self.form_data, user=self.creator)
        self.assertTrue(form.is_valid())
        self.assertIn(group, form.fields['groups'].queryset)

    def test_create_event_form_without_user_groups(self):
        form = CreateEventForm(data=self.form_data, user=self.creator)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.fields['groups'].queryset.count(), 0)


   
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