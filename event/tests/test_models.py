from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from event.models import Event, EventVisibility, Status, GroupEvent
from main.models import JoinMode
from group.models import Group

class BaseModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.creator = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.event_data = {
            'name': 'Test Event',
            'description': 'This is a test event',
            'visibility': EventVisibility.PUBLIC,
            'join_mode': JoinMode.DIRECT,
            'status': Status.ACTIVE,
            'capacity': 50,
            'location': 'Test Location',
            'start_time': timezone.now(),
            'end_time': timezone.now() + timezone.timedelta(hours=2),
            'creator': self.creator
        }

class EventModelTest(BaseModelTest):
    def test_event_creation(self):
        event = Event.objects.create(**self.event_data)
        self.assertEqual(Event.objects.count(), 1)

        # Assert that all fields match expected data
        self.assertEqual(event.name, self.event_data['name'])
        self.assertEqual(event.description, self.event_data['description'])
        self.assertEqual(event.visibility, self.event_data['visibility'])
        self.assertEqual(event.join_mode, self.event_data['join_mode'])
        self.assertEqual(event.status, self.event_data['status'])
        self.assertEqual(event.capacity, self.event_data['capacity'])
        self.assertEqual(event.location, self.event_data['location'])
        self.assertEqual(event.start_time, self.event_data['start_time'])
        self.assertEqual(event.end_time, self.event_data['end_time'])
        self.assertEqual(event.name, self.event_data['name'])
        self.assertEqual(event.creator, self.creator)

        # Assert that the creator has been added to the event's hosts
        self.assertIn(event.creator, event.hosts.all())

        # Assert that the creator has been added to the event's attendees
        self.assertIn(event.creator, event.attendees.all())

    def test_event_str_method(self):
        event = Event.objects.create(**self.event_data)
        self.assertEqual(str(event), self.event_data['name'])

    def test_event_host_addition(self):
        event = Event.objects.create(**self.event_data)
        User = get_user_model()
        host = User.objects.create_user(
            username='hostuser',
            password='hostpassword'
        )
        event.hosts.add(host)

        # Assert that the host has been added to the event's hosts
        self.assertIn(host, event.hosts.all())
        # Assert that the host has been added to the event's attendees
        self.assertIn(host, event.attendees.all())

class GroupEventModelTest(BaseModelTest):
    def setUp(self):
        super().setUp()
        self.group = Group.objects.create(
        location='Sample Location',
        name='Sample Group',
        description='Sample Description',
        creator=self.creator
        )

        self.group_event_data = {
            "name": "Test Group Event",
            "description": "A test group event",
            "visibility": EventVisibility.PUBLIC,
            "join_mode": JoinMode.DIRECT,
            "status": Status.ACTIVE,
            "capacity": 30,
            "location": "Group Test Location",
            "start_time": timezone.now(),
            "end_time": timezone.now() + timezone.timedelta(hours=2),
            "creator": self.creator,
            "group": self.group,
        }
    
    def test_group_event_creation(self):
        group_event = GroupEvent.objects.create(**self.group_event_data)
        self.assertEqual(GroupEvent.objects.count(), 1)
        self.assertEqual(group_event.group, self.group)

    def test_group_event_inherited_attributes(self):
        group_event = GroupEvent.objects.create(**self.group_event_data)
        self.assertEqual(group_event.visibility, self.group_event_data["visibility"])
        self.assertEqual(group_event.start_time, self.group_event_data["start_time"])

    def test_group_event_creator_as_host(self):
        group_event = GroupEvent.objects.create(**self.group_event_data)
        self.assertTrue(self.creator in group_event.hosts.all())
        self.assertTrue(self.creator in group_event.attendees.all())
