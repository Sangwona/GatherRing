import json
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from event.models import Event, GroupEvent, EventVisibility, Status, EventRequest
from group.models import Group
from main.models import JoinMode
import unittest

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
        response = self.client.post(reverse('create_event_ingroup', args=[str(non_existent_group_id)]), data=self.group_event_form_data)
        # Returns a 404 page when the event is not found
        self.assertEqual(response.status_code, 404)

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

class EventManageTestCase(BaseViewTest):
    def setUp(self):
        User = get_user_model()
        # Create and Log in user
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
            'creator': self.user,
        }
        self.event = Event.objects.create(**self.form_data)
        self.event_request = EventRequest.objects.create(
            event=self.event,
            user=self.user
        )
    
    def test_manage_view_with_invalid_event(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('manage_event', args=['9999']))
        
        # Returns a 404 page when the event is not found
        self.assertEqual(response.status_code, 404)

    def test_manage_event_authenticated(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('manage_event', args=[str(self.event.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/manage.html')
        
        # Check if 'requests' is present in the context
        self.assertIn('requests', response.context)

        # Check the number of join requests in the context
        self.assertEqual(len(response.context['requests']), 1)  
    
    def test_manage_event_unauthenticated(self):
        # Attempt to access the create event page without authentication
        response = self.client.get(reverse('manage_event', args=[str(self.event.id)]))

        # Assert that it redirects to the login page (status code 302)
        self.assertEqual(response.status_code, 302)
        # self.assertRedirects(response, '/user/login/?next=/event/manage/' + str(self.event.id) + '/')
    
    def test_manage_view_without_requests(self):
        empty_event = Event.objects.create(
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

        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('manage_event', args=[str(empty_event.id)]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/manage.html')
        
        # Assert that a message indicating no join requests is present
        self.assertContains(response, 'No requests.')

class EventAttendanceTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword2")
        self.event = Event.objects.create(
            name= 'Test Event',
            description= 'This is a test event',
            visibility= EventVisibility.PUBLIC,
            join_mode= JoinMode.DIRECT,
            status= Status.ACTIVE,
            capacity= 50,
            location= 'Test Location',
            start_time= timezone.now(),
            end_time= timezone.now() + timezone.timedelta(hours=2),
            creator=self.user
        )
        

    def test_toggle_event_attendance_view(self):
        self.client.login(username='testuser2', password='testpassword2')

        # Initial state: User is not a member
        self.assertFalse(self.event.attendees.filter(pk=self.user2.pk).exists())

        # Sending a POST request to join the event
        self.client.post(reverse('toggle_event_attendance', args=[str(self.event.id)]))

        # After joining, the user should be a member
        self.assertTrue(self.event.attendees.filter(pk=self.user2.pk).exists())

        # Sending a second POST request to leave the event
        self.client.post(reverse('toggle_event_attendance', args=[str(self.event.id)]))

        # After leaving, the user should not be a member
        self.assertFalse(self.event.attendees.filter(pk=self.user2.pk).exists())

    def test_toggle_event_attendance_unauthenticated(self):
        # Attempt to join an event unauthenticated
        response = self.client.post(reverse('toggle_event_attendance', args=[str(self.event.id)]))

        # Assert that it redirects to the login page (status code 302)
        self.assertEqual(response.status_code, 302)
        # self.assertRedirects(response, '/user/login/?next=/event/toggle_attendance/' + str(self.event.id) + '/')

    def test_toggle_event_request_view(self):
        self.client.login(username='testuser2', password='testpassword2')

        # Initial state: No event request exists
        self.assertFalse(self.event.requests.filter(user=self.user2).exists())

        # Sending a POST request to create a event request
        self.client.post(reverse('toggle_event_request', args=[str(self.event.id)]))

        # After creating the request, it should exist in the database
        self.assertTrue(self.event.requests.filter(user=self.user2).exists())

        # Sending a second POST request to cancel the request
        self.client.post(reverse('toggle_event_request', args=[str(self.event.id)]))

        # After canceling, the request should no longer exist
        self.assertFalse(self.event.requests.filter(user=self.user2).exists())

    def test_toggle_event_request_unauthenticated(self):
        # Attempt to join a event unauthenticated
        response = self.client.post(reverse('toggle_event_request', args=[str(self.event.id)]))

        # Assert that it redirects to the login page (status code 302)
        self.assertEqual(response.status_code, 302)
        # self.assertRedirects(response, '/user/login/?next=/event/toggle_request/' + str(self.event.id) + '/')

class ShowEventAttendeesTestCase(BaseViewTest):
    def setUp(self):
        super().setUp()  # Call the parent setup to set up common data
        User = get_user_model()
        self.user1 = User.objects.create_user(username="testuser1", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword")
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
            'creator':self.user1
        }
        self.event = Event.objects.create(**self.event_data)
        self.event.attendees.add(self.user2)
        
        self.url = reverse('show_event_attendees', args=[str(self.event.pk)])
        
    def test_show_event_members(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        
        members_data = response.json()
        self.assertEqual(len(members_data), 2)
        
        member1_data = members_data[0]
        self.assertEqual(member1_data['id'], self.user1.id)
        self.assertEqual(member1_data['username'], self.user1.username)
        
        member2_data = members_data[1]
        self.assertEqual(member2_data['id'], self.user2.id)
        self.assertEqual(member2_data['username'], self.user2.username)
    
    def test_event_not_found(self):
        invalid_event_id = 999
        url = reverse('show_event_attendees', args=[str(invalid_event_id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class HandleRequestViewTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.host_user = User.objects.create_user(username='hostuser', password='testpassword')
        self.non_host_user = User.objects.create_user(username='nothostuser', password='testpassword')
        self.event = Event.objects.create(
            name= 'Test Event',
            description= 'This is a test event',
            visibility= EventVisibility.PUBLIC,
            join_mode= JoinMode.DIRECT,
            status= Status.ACTIVE,
            capacity= 50,
            location= 'Test Location',
            start_time= timezone.now(),
            end_time= timezone.now() + timezone.timedelta(hours=2),
            creator=self.host_user
        )
        self.event.hosts.add(self.host_user)
        self.request = EventRequest.objects.create(user=self.non_host_user, event=self.event)

    def test_handle_request_accept(self):
        self.client.login(username='hostuser', password='testpassword')

        response = self.client.post(reverse('handle_event_request', args=[str(self.request.id)]), {
            'action': 'accept'
        }, content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"message": "success"})

        # Check that user was added to attendees
        self.assertTrue(self.non_host_user in self.event.attendees.all())
        # Check that the request was deleted
        with self.assertRaises(EventRequest.DoesNotExist):
            EventRequest.objects.get(pk=self.request.id)

    def test_handle_request_reject(self):
        self.client.login(username='hostuser', password='testpassword')

        response = self.client.post(reverse('handle_event_request', args=[str(self.request.id)]), {
            'action': 'reject'
        }, content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"message": "success"})

        # Check that user was not added to attendees
        self.assertFalse(self.non_host_user in self.event.attendees.all())
        # Check that the request was deleted
        with self.assertRaises(EventRequest.DoesNotExist):
            EventRequest.objects.get(pk=self.request.id)

    def test_handle_request_non_host(self):
        # Login as a different user who is not a host
        self.client.login(username='nothostuser', password='testpassword')

        # Send a POST request to accept the request
        response = self.client.post(reverse('handle_event_request', args=[str(self.request.id)]), {
            'action': 'accept'
        }, content_type='application/json')

        # Check that the response is a PermissionDenied error
        self.assertEqual(response.status_code, 403)

        # Check that user was not added to attendees
        self.assertFalse(self.non_host_user in self.event.attendees.all())

class ChangeStatusEventTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.event = Event.objects.create(
            name= 'Test Event',
            description= 'This is a test event',
            visibility= EventVisibility.PUBLIC,
            join_mode= JoinMode.DIRECT,
            status= Status.ACTIVE,
            capacity= 50,
            location= 'Test Location',
            start_time= timezone.now(),
            end_time= timezone.now() + timezone.timedelta(hours=2),
            creator=self.user
        )

    def test_change_status_active(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Define the data for the request
        data = {'action': 'reactive'}
        url = reverse('change_status_event', args=[str(self.event.pk)])

        # Make a POST request to change the status to ACTIVE
        response = self.client.post(url, json.dumps(data), content_type='application/json')

        # Check if the response is successful (status code 200)
        self.assertEqual(response.status_code, 200)

        # Check if the event status has changed to ACTIVE
        self.event.refresh_from_db()
        self.assertEqual(self.event.status, Status.ACTIVE)

        # Check if the response data contains 'isActive' as True
        response_data = json.loads(response.content)
        self.assertTrue(response_data['isActive'])

    def test_change_status_cancel(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Define the data for the request
        data = {'action': 'cancel'}
        url = reverse('change_status_event', args=[str(self.event.pk)])

        # Make a POST request to change the status to CANCELED
        response = self.client.post(url, json.dumps(data), content_type='application/json')

        # Check if the response is successful (status code 200)
        self.assertEqual(response.status_code, 200)

        # Check if the event status has changed to CANCELED
        self.event.refresh_from_db()
        self.assertEqual(self.event.status, Status.CANCELED)

        # Check if the response data contains 'isActive' as False
        response_data = json.loads(response.content)
        self.assertFalse(response_data['isActive'])