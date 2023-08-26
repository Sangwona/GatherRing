from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from event.models import Event, GroupEvent, EventVisibility, Status
from group.models import Group
from main.models import JoinMode

class BaseViewTest(TestCase):
    def setUp(self):
        User = get_user_model()
        # Create and Log in user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
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

class CreateEventViewTest(BaseViewTest):
    def test_create_event_view_GET(self):
        # Test the create event view with a GET request
        response = self.client.get(reverse('create_event'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/create.html')

    def test_create_event_view_valid_POST(self):
        # Test the create event view with a valid POST request
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
        invalid_data.pop('name')
        response = self.client.post(reverse('create_event'), data=invalid_data)

        self.assertEqual(response.status_code, 200)  # Form submission should return a 200
        self.assertTemplateUsed(response, 'event/create.html')

        # Check if the form has errors
        self.assertFormError(response, 'form', 'name', 'This field is required.')

class CreateGroupEventViewTest(BaseViewTest):
    def setUp(self):
        super().setUp()  # Call the parent setup to set up common data
        self.group = Group.objects.create(
            location='Sample Location',
            name='Sample Group',
            description='Sample Description',
            creator=self.user
        )

        self.group_event_form_data = self.form_data.copy()
        self.group_event_form_data['group'] = self.group

    def test_create_group_event_view_GET(self):
        response = self.client.get(reverse('create_event_ingroup', args=[str(self.group.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/create_ingroup.html')

    def test_create_group_event_view_POST_valid_form(self):
        response = self.client.post(reverse('create_event_ingroup', args=[str(self.group.id)]), data=self.group_event_form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/profile.html')

        # Check if the event was created and associated with the user
        group_event = GroupEvent.objects.first()
        self.assertIsNotNone(group_event)
        self.assertEqual(group_event.name, 'Test Event')
        self.assertEqual(group_event.creator, self.user)

    def test_create_group_event_view_POST_group_not_found(self):
        non_existent_group_id = 9999  # An ID that does not exist in your database
        with self.assertRaises(ObjectDoesNotExist):  # Should raise an exception
            self.client.post(reverse('create_event_ingroup', args=[str(non_existent_group_id)]), data=self.group_event_form_data)

    def test_create_group_event_view_POST_invalid_form(self):
        invalid_data = self.form_data.copy()
        invalid_data.pop('name')

        response = self.client.post(reverse('create_event_ingroup', args=[str(self.group.id)]), data=invalid_data)
        self.assertEqual(response.status_code, 200)  # Form submission should return a 200
        self.assertTemplateUsed(response, 'event/create_ingroup.html')
       
        # Check if the form has errors
        self.assertFormError(response, 'form', 'name', 'This field is required.')

class EventProfileViewTest(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.event_data = {
            'name':'Test Event',
            'description':'This is a test event',
            'visibility':EventVisibility.PUBLIC,
            'join_mode':JoinMode.DIRECT,
            'status':Status.ACTIVE,
            'capacity':50,
            'location':'Test Location',
            'start_time':timezone.now(),
            'end_time':timezone.now() + timezone.timedelta(hours=2),
            'creator':self.user
        }
        self.event = Event.objects.create(**self.event_data)

        self.group1 = Group.objects.create(
            name="Test Group",
            description="This is a test group",
            location="Test Location",
            visibility="Public",
            join_mode="Direct",
            capacity=50,
            creator=self.user,
        )

        self.groupevent_data = self.event_data.copy()
        self.groupevent_data['group'] = self.group1
        self.groupevent = GroupEvent.objects.create(**self.groupevent_data)

    def test_group_event_profile_view_GET(self):
        response = self.client.get(reverse('event_profile', args=[str(self.groupevent.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/profile.html')
        
    def test_event_profile_view_GET(self):
        response = self.client.get(reverse('event_profile', args=[str(self.event.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/profile.html')

class AllEventViewTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        Event.objects.create(
            name='Test Event 1',
            description='This is a test event 1',
            visibility=EventVisibility.PUBLIC,
            join_mode=JoinMode.DIRECT,
            creator=self.user,
            capacity=50,
            location='Test Location',
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=2)
        )
        Event.objects.create(
            name='Test Event 2',
            description='This is a test event 2',
            visibility=EventVisibility.PUBLIC,
            join_mode=JoinMode.DIRECT,
            creator=self.user,
            capacity=50,
            location='Test Location',
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=2)
        )

    def test_all_events_view_GET(self):
        response = self.client.get(reverse('all_events'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/all.html')
        self.assertContains(response, 'Test Event 1')  # Check if event names are present
        self.assertContains(response, 'Test Event 2')    

class EditEventViewTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
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
            'creator': self.user,
        }
        self.event = Event.objects.create(**self.form_data)
        
    def test_edit_event_view_GET(self):
        response = self.client.get(reverse('edit_event', args=[str(self.event.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/edit.html')

    def test_edit_event_view_valid_POST(self):
        updated_data = self.form_data.copy()
        updated_data['hosts'] = [self.user.pk]
        updated_data['name'] = 'Updated Name'
        response = self.client.post(reverse('edit_event', args=[str(self.event.id)]), updated_data)
        self.assertEqual(response.status_code, 200)  # Successful form submission should return a 200

        #check if the event was updated
        updated_event = Event.objects.get(pk=self.event.id)
        self.assertEqual(updated_event.name, 'Updated Name')

    def test_edit_event_view_invalid_POST(self):
        invalid_data = self.form_data.copy() # missing hosts
        response = self.client.post(reverse('edit_event', args=[str(self.event.id)]), invalid_data)
        self.assertEqual(response.status_code, 200)
        #should render the form with errors
        self.assertTemplateUsed(response, 'event/edit.html')
        # Check if the form has errors
        self.assertFormError(response, 'form', 'hosts', 'This field is required.')

class EditGroupEventViewTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        self.group = Group.objects.create(
            location='Sample Location',
            name='Sample Group',
            description='Sample Description',
            creator=self.user
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
            'creator': self.user,
            'group' : self.group  
        }
        self.group_event = GroupEvent.objects.create(**self.form_data)
        
    def test_edit_group_event_view_GET(self):
        response = self.client.get(reverse('edit_event', args=[str(self.group_event.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/edit.html')

    def test_edit_group_event_view_valid_POST(self):
        updated_data = self.form_data.copy()
        updated_data['hosts'] = [self.user.pk]
        updated_data['name'] = 'Updated Name'
        response = self.client.post(reverse('edit_event', args=[str(self.group_event.id)]), updated_data)
        self.assertEqual(response.status_code, 200)  # Successful form submission should return a 200
        
        #check if the event was updated
        updated_event = GroupEvent.objects.get(pk=self.group_event.id)
        self.assertEqual(updated_event.name, 'Updated Name')

    def test_edit_group_event_view_invalid_POST(self):
        invalid_data = self.form_data.copy() # missing hosts
        response = self.client.post(reverse('edit_event', args=[str(self.group_event.id)]), invalid_data)
        self.assertEqual(response.status_code, 200)
        #should render the form with errors
        self.assertTemplateUsed(response, 'event/edit.html')
        # Check if the form has errors
        self.assertFormError(response, 'form', 'hosts', 'This field is required.')