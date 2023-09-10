import json
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from event.models import Event, GroupEvent, EventVisibility, Status, EventRequest
from group.models import Group
from main.models import JoinMode, Photo

class BaseViewTest(TestCase):
    def setUp(self):
        User = get_user_model()
        # Create user without groups
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Create user that is group admin
        self.group_admin = User.objects.create_user(username='testadmin', password='testpassword')
        self.group = Group.objects.create(
            location='Sample Location',
            name='Sample Group',
            description='Sample Description',
            creator=self.group_admin
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

class EventCreateViewTest(BaseViewTest):
    # GET Cases
    def test_create_event_no_group_id(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('create_event'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/create.html') 

    def test_create_event_with_group_id_as_admin(self):
        self.client.login(username='testadmin', password='testpassword')
        response = self.client.get(reverse('create_event', args=[str(self.group.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/create.html')
        self.assertEqual(response.context['group'], self.group)
    
    def test_create_event_with_group_id_not_admin(self):
        # Login as a user who is not an admin
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('create_event', args=[str(self.group.id)]))
        # Check that the response is a PermissionDenied error
        self.assertEqual(response.status_code, 403)

    def test_create_event_unauthenticated(self):
        # Attempt to access the create event page without authentication
        response = self.client.get(reverse('create_event'))

        # Assert that it redirects to the login page (status code 302)
        self.assertEqual(response.status_code, 302)
        # self.assertRedirects(response, '/user/login/?next=/event/create/') 
    
    # POST Cases
    def test_create_event_valid_form_no_groups(self):
        # Test the create event view with a valid POST request
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('create_event'), data=self.form_data)
        self.assertEqual(response.status_code, 200)  # Successful form submission should return a 200
        self.assertTemplateUsed(response, 'event/profile.html')

        # Check if the event was created and associated with the user
        event = Event.objects.first()
        self.assertIsNotNone(event)
        self.assertEqual(event.name, 'Test Event')
        self.assertEqual(event.creator, self.user)
    
    def test_create_event_valid_form_with_groups(self):
        # Test the create event view with a valid POST request
        self.client.login(username='testadmin', password='testpassword')
        group_data = self.form_data.copy()
        group_data['groups'] = [self.group.id]
        response = self.client.post(reverse('create_event'), data=group_data)
        self.assertEqual(response.status_code, 200)  # Successful form submission should return a 200
        self.assertTemplateUsed(response, 'event/profile.html')

        # Check if the event was created and associated with the user
        groupEvent = GroupEvent.objects.first()
        self.assertIsNotNone(groupEvent)
        self.assertEqual(groupEvent.name, 'Test Event')
        self.assertEqual(groupEvent.creator, self.group_admin)
        self.assertEqual(self.group, groupEvent.group)

    def test_create_event_invalid_form(self):
        # Test the create event view with an invalid POST request (missing required fields)
        self.client.login(username='testuser', password='testpassword')
        invalid_data = self.form_data.copy()
        invalid_data.pop('name')
        response = self.client.post(reverse('create_event'), data=invalid_data)

        self.assertEqual(response.status_code, 200)  # Form submission should return a 200
        self.assertTemplateUsed(response, 'event/create.html')

        # Check if the form has errors
        self.assertFormError(response, 'form', 'name', 'This field is required.')

class BaseViewTest2(BaseViewTest):
    def setUp(self):
        super().setUp()
        # Create event with creator set as self.user
        self.event_data = self.form_data.copy()
        self.event_data['creator'] = self.user
        self.event = Event.objects.create(**self.event_data)

        # Create groupEvent with creator set as self.group_admin
        self.groupevent_data = self.form_data.copy()
        self.groupevent_data['creator'] = self.group_admin
        self.groupevent_data['group'] = self.group
        self.groupevent = GroupEvent.objects.create(**self.groupevent_data)

        # Create new user that is not in any group or hosting any events
        self.user2 = get_user_model().objects.create_user(username='testuser2', password='testpassword2')
        
class EventProfileViewTest(BaseViewTest2):
    def test_group_event_profile_view_GET(self):
        response = self.client.get(reverse('event_profile', args=[str(self.groupevent.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/profile.html')
        
    def test_event_profile_view_GET(self):
        response = self.client.get(reverse('event_profile', args=[str(self.event.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/profile.html')

class EventAllViewTest(BaseViewTest2):
    def test_all_events_view_GET(self):
        response = self.client.get(reverse('all_events'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/all.html')
        self.assertContains(response, 'Test Event')  # Check if event names are present

class EventEditViewTest(BaseViewTest2):
    # GET Cases
    def test_edit_event_as_host(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('edit_event', args=[str(self.event.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/edit.html')
    
    def test_edit_event_not_host(self):
        # Login as a user who is not a host
        self.client.login(username='testuser2', password='testpassword2')
        response = self.client.get(reverse('edit_event', args=[str(self.event.id)]))
        # Check that the response is a PermissionDenied error
        self.assertEqual(response.status_code, 403)

    def test_edit_event_unauthenticated(self):
        # Attempt to access the edit event page without authentication
        response = self.client.get(reverse('edit_event', args=[str(self.event.id)]))

        # Assert that it redirects to the login page (status code 302)
        self.assertEqual(response.status_code, 302)
    
    # POST Cases
    def test_edit_event_view_valid_POST(self):
        self.client.login(username='testuser', password='testpassword')
        updated_data = self.form_data.copy()
        updated_data['hosts'] = [self.user.pk]
        updated_data['name'] = 'Updated Name'
        response = self.client.post(reverse('edit_event', args=[str(self.event.id)]), updated_data)
        self.assertEqual(response.status_code, 200)  # Successful form submission should return a 200

        #check if the event was updated
        updated_event = Event.objects.get(pk=self.event.id)
        self.assertEqual(updated_event.name, 'Updated Name')

    def test_edit_event_view_invalid_POST(self):
        self.client.login(username='testuser', password='testpassword')
        invalid_data = self.form_data.copy() # missing hosts
        response = self.client.post(reverse('edit_event', args=[str(self.event.id)]), invalid_data)
        self.assertEqual(response.status_code, 200)
        #should render the form with errors
        self.assertTemplateUsed(response, 'event/edit.html')
        # Check if the form has errors
        self.assertFormError(response, 'form', 'hosts', 'This field is required.')

class EventManageViewTest(BaseViewTest2):
    def setUp(self):
        super().setUp()
        self.event_request = EventRequest.objects.create(
            event=self.event,
            user=self.user2
        )
    
    def test_manage_event_invalid_event(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('manage_event', args=['9999']))
        
        # Returns a 404 page when the event is not found
        self.assertEqual(response.status_code, 404)

    def test_manage_event_as_host_one_request(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('manage_event', args=[str(self.event.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event/manage.html')
        # Check if 'requests' is present in the context
        self.assertIn('requests', response.context)
        # Check the number of join requests in the context
        self.assertEqual(len(response.context['requests']), 1)
    
    def test_manage_event_as_host_no_requests(self):
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
        # Check if 'requests' is present in the context
        self.assertIn('requests', response.context)
        # Check the number of join requests in the context
        self.assertEqual(len(response.context['requests']), 0)
    
    def test_manage_event_not_host(self):
        # Login as a user who is not a host
        self.client.login(username='testuser2', password='testpassword2')
        response = self.client.get(reverse('manage_event', args=[str(self.event.id)]))
        # Check that the response is a PermissionDenied error
        self.assertEqual(response.status_code, 403)

    def test_manage_event_unauthenticated(self):
        # Attempt to access the manage event page without authentication
        response = self.client.get(reverse('manage_event', args=[str(self.event.id)]))

        # Assert that it redirects to the login page (status code 302)
        self.assertEqual(response.status_code, 302)

class EventAttendanceViewTest(BaseViewTest2):
    def test_toggle_event_attendance_view(self):
        self.client.login(username='testuser2', password='testpassword2')

        # Initial state: User is not an attendee
        self.assertFalse(self.event.attendees.filter(pk=self.user2.pk).exists())

        # Sending a POST request to join the event
        self.client.post(reverse('toggle_event_attendance', args=[str(self.event.id)]))

        # After joining, the user should be an attendee
        self.assertTrue(self.event.attendees.filter(pk=self.user2.pk).exists())

        # Sending a second POST request to leave the event
        self.client.post(reverse('toggle_event_attendance', args=[str(self.event.id)]))

        # After leaving, the user should not be an attendee
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

class ShowEventAttendeesViewTest(BaseViewTest2):
    def setUp(self):
        super().setUp()  # Call the parent setup to set up common data
        self.event.attendees.add(self.user2)
        self.url = reverse('show_event_attendees', args=[str(self.event.pk)])
        
    def test_show_event_members(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        
        members_data = response.json()
        self.assertEqual(len(members_data), 2)
        
        member1_data = members_data[0]
        self.assertEqual(member1_data['id'], self.user.id)
        self.assertEqual(member1_data['username'], self.user.username)
        
        member2_data = members_data[1]
        self.assertEqual(member2_data['id'], self.user2.id)
        self.assertEqual(member2_data['username'], self.user2.username)
    
    def test_event_not_found(self):
        invalid_event_id = 999
        url = reverse('show_event_attendees', args=[str(invalid_event_id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class EventHandleRequestViewTest(BaseViewTest2):
    def setUp(self):
        super().setUp()
        self.event_request = EventRequest.objects.create(
            event=self.event,
            user=self.user2
        )

    def test_handle_request_accept(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.post(reverse('handle_event_request', args=[str(self.event_request.id)]), {
            'action': 'accept'
        }, content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"message": "success"})

        # Check that user was added to attendees
        self.assertTrue(self.user2 in self.event.attendees.all())
        # Check that the request was deleted
        with self.assertRaises(EventRequest.DoesNotExist):
            EventRequest.objects.get(pk=self.event_request.id)

    def test_handle_request_reject(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.post(reverse('handle_event_request', args=[str(self.event_request.id)]), {
            'action': 'reject'
        }, content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"message": "success"})

        # Check that user was not added to attendees
        self.assertFalse(self.user2 in self.event.attendees.all())
        # Check that the request was deleted
        with self.assertRaises(EventRequest.DoesNotExist):
            EventRequest.objects.get(pk=self.event_request.id)

    def test_handle_request_non_host(self):
        # Login as a different user who is not a host
        self.client.login(username='testuser2', password='testpassword2')

        # Send a POST request to accept the request
        response = self.client.post(reverse('handle_event_request', args=[str(self.event_request.id)]), {
            'action': 'accept'
        }, content_type='application/json')

        # Check that the response is a PermissionDenied error
        self.assertEqual(response.status_code, 403)

        # Check that user was not added to attendees
        self.assertFalse(self.user2 in self.event.attendees.all())

    def test_handle_request_unauthenticated(self):
        # Send a POST request to accept the request
        response = self.client.post(reverse('handle_event_request', args=[str(self.event_request.id)]), {
            'action': 'accept'
        }, content_type='application/json')

        # Assert that it redirects to the login page (status code 302)
        self.assertEqual(response.status_code, 302)

class EventChangeStatusViewTest(BaseViewTest2):
    def test_change_status_active(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Define the data for the request
        data = {'action': 'reactive'}
        url = reverse('change_status_event', args=[str(self.event.pk)])

        # Make a POST request to change the status to ACTIVE
        response = self.client.post(url, json.dumps(data), content_type='application/json')

        # Check if the response is successful (status code 200)
        self.assertEqual(response.status_code, 201)

        # Check if the event status has changed to ACTIVE
        self.event.refresh_from_db()
        self.assertEqual(self.event.status, Status.ACTIVE)

    def test_change_status_cancel(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Define the data for the request
        data = {'action': 'cancel'}
        url = reverse('change_status_event', args=[str(self.event.pk)])

        # Make a POST request to change the status to CANCELED
        response = self.client.post(url, json.dumps(data), content_type='application/json')

        # Check if the response is successful (status code 200)
        self.assertEqual(response.status_code, 201)

        # Check if the event status has changed to CANCELED
        self.event.refresh_from_db()
        self.assertEqual(self.event.status, Status.CANCELED)

    def test_change_status_unauthenticated(self):
        # Define the data for the request
        data = {'action': 'cancel'}
        url = reverse('change_status_event', args=[str(self.event.pk)])

        # Make a POST request to change the status to CANCELED
        response = self.client.post(url, json.dumps(data), content_type='application/json')

        # Assert that it redirects to the login page (status code 302)
        self.assertEqual(response.status_code, 302)

class EventDeleteViewTest(BaseViewTest2):
    def test_delete_event_success(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Send a POST request to delete the event
        response = self.client.post(reverse('delete_event', args=[str(self.event.id)]))

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the event was deleted
        self.assertFalse(Event.objects.filter(pk=self.event.id).exists())

    def test_delete_event_failure(self):
        # Log in a different user (not the creator of the event)
        self.client.login(username='testuser2', password='testpassword2')

        # Send a POST request to delete the event
        response = self.client.post(reverse('delete_event', args=[str(self.event.id)]))

        # Check if the response status code is 403 (Forbidden)
        self.assertEqual(response.status_code, 403)

        # Check if the event still exists
        self.assertTrue(Event.objects.filter(pk=self.event.id).exists())

    def test_delete_event_not_logged_in(self):
        # Send a POST request to delete the event without logging in
        response = self.client.post(reverse('delete_event', args=[str(self.event.id)]))

        # Check if the response status code is 302 (Redirect to login)
        self.assertEqual(response.status_code, 302)

        # Check if the event still exists
        self.assertTrue(Event.objects.filter(pk=self.event.id).exists())

class EventAddPhotoViewTest(BaseViewTest2):
    def test_add_photo_authenticated_attendee(self):
        self.client.login(username='testuser', password='testpassword')
        uploaded_file = SimpleUploadedFile(
            'test_photo.jpg', b'file_content', content_type='image/jpeg'
        )
        response = self.client.post(reverse('add_event_photo', args=[str(self.event.id)]), data={'photo': uploaded_file})
        # Check that the response redirects to the event profile page
        self.assertRedirects(response, reverse('event_profile', args=[str(self.event.id)]))
        # Check that a photo object is created and associated with the event
        self.assertEqual(self.event.photos.count(), 1)
        photo = self.event.photos.all().first()
        self.assertEqual(photo.uploaded_by, self.user)
        self.assertEqual(photo.related_event, self.event)
        self.assertEqual(photo.photo.name, 'photos/test_photo.jpg')
        photo.delete()
        
    def test_add_photo_authenticated_non_attendee(self):
        # Log in as user who is not an attendee
        self.client.login(username='testuser2', password='testpassword2')
        self.uploaded_file = SimpleUploadedFile(
            'test_photo.jpg', b'file_content', content_type='image/jpeg'
        )
        response = self.client.post(reverse('add_event_photo', args=[str(self.event.id)]), data={'photo': self.uploaded_file})
        # Check that the response is a PermissionDenied error
        self.assertEqual(response.status_code, 403)
        # Check that no photo object is created
        self.assertFalse(Photo.objects.filter(related_event=self.event).exists())
        self.assertEqual(self.event.photos.count(), 0)

    def test_add_photo_unauthenticated(self):
        self.uploaded_file = SimpleUploadedFile(
            'test_photo.jpg', b'file_content', content_type='image/jpeg'
        )
        # Create a POST request to add a photo without logging in
        response = self.client.post(reverse('add_event_photo', args=[str(self.event.id)]), data={'photo': self.uploaded_file})
        
        # Assert that it redirects to the login page (status code 302)
        self.assertEqual(response.status_code, 302)
        
        # Check that no photo object is created
        self.assertFalse(Photo.objects.filter(related_event=self.event).exists())
        self.assertEqual(self.event.photos.count(), 0)

class EventIsAttendeeViewTest(BaseViewTest2):
    def test_is_attendee_authenticated_and_attendee(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('event_is_attendee', args=[str(self.event.id)]))
        self.assertEqual(response.status_code, 200)  # Expect a successful response
        data = response.json()
        self.assertTrue(data['is_attendee'])  # The user should be an attendee
    
    def test_is_attendee_authenticated_not_attending(self):
        self.client.login(username='testuser2', password='testpassword2')
        response = self.client.get(reverse('event_is_attendee', args=[str(self.event.id)]))
        self.assertEqual(response.status_code, 200)  # Expect a successful response
        data = response.json()
        self.assertFalse(data['is_attendee'])  # The user should not be an attendee

    def test_is_attendee_unauthenticated(self):
        response = self.client.get(reverse('event_is_attendee', args=[str(self.event.id)]))
        self.assertEqual(response.status_code, 200)  # Expect a successful response
        data = response.json()
        self.assertFalse(data['is_attendee'])  # The user should not be an attendee

class EventGetPhotosViewTest(BaseViewTest2):
    def test_get_photos_with_photos(self):
        self.photo1 = Photo.objects.create(
            uploaded_by=self.user,
            photo=SimpleUploadedFile('photo1.jpg', b'photo_content', content_type='image/jpeg'),
            related_event = self.event
        )
        self.photo2 = Photo.objects.create(
            uploaded_by=self.user,
            photo=SimpleUploadedFile('photo2.jpg', b'photo_content', content_type='image/jpeg'),
            related_event = self.event
        )
        self.event.photos.add(self.photo1, self.photo2)

        response = self.client.get(reverse('get_event_photos', args=[str(self.event.id)]))
        self.assertEqual(response.status_code, 200)  # Expect a successful response
        data = response.json()
        self.assertIn('photos', data)  # Check if 'photos' key exists in the JSON response
        self.assertEqual(len(data['photos']), 2)  # Check if there are 2 photos in the response
        self.photo1.delete()
        self.photo2.delete()

    def test_get_photos_no_photos(self):
        response = self.client.get(reverse('get_event_photos', args=[str(self.event.id)]))
        self.assertEqual(response.status_code, 200)  # Expect a successful response
        data = response.json()
        self.assertIn('photos', data)  # Check if 'photos' key exists in the JSON response
        self.assertEqual(len(data['photos']), 0)  # Check if there are no photos in the response