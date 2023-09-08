from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from group.models import Group, GroupRequest
from main.models import Interest, Photo

class CreateGroupFormWizardTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpassword")

        self.interest1 = Interest.objects.create(name='Interest 1')
        self.interest2 = Interest.objects.create(name='Interest 2')

    def test_group_creation(self):
        self.client.login(username='testuser', password='testpassword')
        form_steps_data = [
            ('0', {'0-location': 'Test Location'}),
            ('1', {'1-interests': [self.interest1.pk, self.interest2.pk]}),
            ('2', {'2-name': 'Test Group'}),
            ('3', {'3-description': 'Test Description'})
        ]
        for step, data in form_steps_data:
            data['create_group_form_wizard-current_step'] = step
            response = self.client.post(reverse('create_group'), data)
            if step == '3':
                self.assertEqual(response.status_code, 302) # Expecting a redirect after last step
            else:
                self.assertEqual(response.status_code, 200) #intermediate steps should return 200 code

        # Check if the group was created
        self.assertEqual(Group.objects.count(), 1)
        group = Group.objects.first()
        self.assertEqual(group.location, form_steps_data[0][1]['0-location'])
        self.assertEqual(group.name, form_steps_data[2][1]['2-name'])
        self.assertEqual(group.description, form_steps_data[3][1]['3-description'])
        self.assertEqual(group.creator, self.user)
        self.assertEqual(list(group.interests.values_list('id', flat=True)), form_steps_data[1][1]['1-interests'])

        self.assertEqual(response['Location'], reverse('group_profile', args=[str(group.pk)]))  # Check the redirection URL

    def test_create_group_unauthenticated(self):
        # Attempt to access the create group page without authentication
        response = self.client.get(reverse('create_group'))

        # Assert that it redirects to the login page (status code 302)
        self.assertEqual(response.status_code, 302)
        # self.assertRedirects(response, '/user/login/?next=/group/create/')

class BaseViewTest(TestCase):
    def setUp(self):
        # Create a user as group creator
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpassword")

        # Create a second user
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword2")

        # Create a group
        self.group = Group.objects.create(
            name="Test Group",
            description="This is a test group",
            location="Test Location",
            visibility="Public",
            join_mode="Direct",
            capacity=50,
            creator=self.user,
        )

class GroupProfileViewTest(BaseViewTest):
    def test_group_profile_view(self):
        response = self.client.get(reverse('group_profile', args=[str(self.group.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.group.name)
        self.assertContains(response, self.group.description)

class GroupAllViewTest(BaseViewTest):
    def test_all_view_with_groups(self):
        self.group2 = Group.objects.create(
            name="Test Group2",
            description="This is a test group2",
            location="Test Location2",
            visibility="Public",
            join_mode="Direct",
            capacity=50,
            creator=self.user,
        )

        response = self.client.get(reverse('all_groups'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group/all.html')
        # Check if groups are passed to the context
        self.assertQuerysetEqual(
            response.context['groups'],
            [self.group, self.group2],
            ordered=False  # The order of groups doesn't matter
        )

    def test_all_view_without_groups(self):
        Group.objects.all().delete()  # Delete all groups
        response = self.client.get(reverse('all_groups'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group/all.html')  
        # Check if an empty queryset is passed to the context
        self.assertQuerysetEqual(response.context['groups'], [])

class GroupEditViewTest(BaseViewTest):
    def test_edit_group_as_admin(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('edit_group', args=[str(self.group.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group/edit.html')
    
    def test_edit_group_not_admin(self):
        # Login as a user who is not an admin
        self.client.login(username='testuser2', password='testpassword2')
        response = self.client.get(reverse('edit_group', args=[str(self.group.id)]))
        # Check that the response is a PermissionDenied error
        self.assertEqual(response.status_code, 403)

    def test_edit_group_unauthenticated(self):
        # Attempt to access the edit group page without authentication
        response = self.client.get(reverse('edit_group', args=[str(self.group.id)]))

        # Assert that it redirects to the login page (status code 302)
        self.assertEqual(response.status_code, 302)
        # self.assertRedirects(response, '/user/login/?next=/group/edit/' + str(self.group.id) + '/')
        
    def test_edit_group_post_valid_data(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('edit_group', args=[str(self.group.id)]), data = {
            'name': 'New Group Name',
            'description': 'new_description',
            'location': 'new_location',
            'visibility' : "Public",
            'join_mode':"Direct",
            'capacity':25,
            'admins': [self.user.pk]
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('group_profile', args=[str(self.group.id)]))
        self.group.refresh_from_db()
        self.assertEqual(self.group.name, 'New Group Name')

    def test_edit_group_post_invalid_data(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('edit_group', args=[self.group.id]), data = {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group/edit.html')
        self.assertIn('form', response.context)

class GroupManageViewTest(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.group_request = GroupRequest.objects.create(
            group=self.group,
            user=self.user2
        )
    
    def test_manage_view_with_invalid_group(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('manage_group', args=['9999']))
        
        # Returns a 404 page when the group is not found
        self.assertEqual(response.status_code, 404)

    def test_manage_group_as_admin_one_request(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('manage_group', args=[str(self.group.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group/manage.html')
        # Check if 'requests' is present in the context
        self.assertIn('requests', response.context)
        # Check the number of join requests in the context
        self.assertEqual(len(response.context['requests']), 1)  
    
    def test_manage_group_as_admin_no_requests(self):
        self.client.login(username='testuser', password='testpassword')
        empty_group = Group.objects.create(
            name='Empty Group',
            description='This group has no join requests.',
            location='Test Location',
            creator=self.user
        )
        response = self.client.get(reverse('manage_group', args=[str(empty_group.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group/manage.html')
        # Check if 'requests' is present in the context
        self.assertIn('requests', response.context)
        # Check the number of join requests in the context
        self.assertEqual(len(response.context['requests']), 0)  

    def test_manage_group_not_admin(self):
        # Login as a user who is not an admin
        self.client.login(username='testuser2', password='testpassword2')
        response = self.client.get(reverse('manage_group', args=[str(self.group.id)]))
        # Check that the response is a PermissionDenied error
        self.assertEqual(response.status_code, 403)

    def test_manage_group_unauthenticated(self):
        # Attempt to access the create group page without authentication
        response = self.client.get(reverse('manage_group', args=[str(self.group.id)]))

        # Assert that it redirects to the login page (status code 302)
        self.assertEqual(response.status_code, 302)
        # self.assertRedirects(response, '/user/login/?next=/group/manage/' + str(self.group.id) + '/')

class GroupMembershipViewTest(BaseViewTest):
    def test_toggle_group_membership_view(self):
        self.client.login(username='testuser2', password='testpassword2')

        # Initial state: User is not a member
        self.assertFalse(self.group.members.filter(pk=self.user2.pk).exists())

        # Sending a POST request to join the group
        self.client.post(reverse('toggle_group_membership', args=[str(self.group.id)]))

        # After joining, the user should be a member
        self.assertTrue(self.group.members.filter(pk=self.user2.pk).exists())

        # Sending a second POST request to leave the group
        self.client.post(reverse('toggle_group_membership', args=[str(self.group.id)]))

        # After leaving, the user should not be a member
        self.assertFalse(self.group.members.filter(pk=self.user2.pk).exists())
    
    def test_toggle_group_membership_unauthenticated(self):
        # Attempt to join a group unauthenticated
        response = self.client.post(reverse('toggle_group_membership', args=[str(self.group.id)]))

        # Assert that it redirects to the login page (status code 302)
        self.assertEqual(response.status_code, 302)
        # self.assertRedirects(response, '/user/login/?next=/group/toggle_membership/' + str(self.group.id) + '/')

    def test_toggle_group_request_view(self):
        self.client.login(username='testuser2', password='testpassword2')

        # Initial state: No group request exists
        self.assertFalse(self.group.requests.filter(user=self.user2).exists())

        # Sending a POST request to create a group request
        self.client.post(reverse('toggle_group_request', args=[str(self.group.id)]))

        # After creating the request, it should exist in the database
        self.assertTrue(self.group.requests.filter(user=self.user2).exists())

        # Sending a second POST request to cancel the request
        self.client.post(reverse('toggle_group_request', args=[str(self.group.id)]))

        # After canceling, the request should no longer exist
        self.assertFalse(self.group.requests.filter(user=self.user2).exists())

    def test_toggle_group_request_unauthenticated(self):
        # Attempt to join a group unauthenticated
        response = self.client.post(reverse('toggle_group_request', args=[str(self.group.id)]))

        # Assert that it redirects to the login page (status code 302)
        self.assertEqual(response.status_code, 302)
        # self.assertRedirects(response, '/user/login/?next=/group/toggle_request/' + str(self.group.id) + '/')

class ShowGroupMembersViewTest(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.group.members.add(self.user2)
        self.url = reverse('show_group_members', args=[str(self.group.pk)])
        
    def test_show_group_members(self):
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
    
    def test_group_not_found(self):
        invalid_group_id = 999
        url = reverse('show_group_members', args=[str(invalid_group_id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class GroupHandleRequestViewTest(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.request = GroupRequest.objects.create(user=self.user2, group=self.group)

    def test_handle_request_accept(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.post(reverse('handle_group_request', args=[str(self.request.id)]), {
            'action': 'accept'
        }, content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"message": "success"})

        # Check that user was added to members
        self.assertTrue(self.user2 in self.group.members.all())
        # Check that the request was deleted
        with self.assertRaises(GroupRequest.DoesNotExist):
            GroupRequest.objects.get(pk=self.request.id)

    def test_handle_request_reject(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.post(reverse('handle_group_request', args=[str(self.request.id)]), {
            'action': 'reject'
        }, content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"message": "success"})

        # Check that user was not added to members
        self.assertFalse(self.user2 in self.group.members.all())
        # Check that the request was deleted
        with self.assertRaises(GroupRequest.DoesNotExist):
            GroupRequest.objects.get(pk=self.request.id)

    def test_handle_request_non_admin(self):
        # Login as a different user who is not an admin
        self.client.login(username='testuser2', password='testpassword2')

        # Send a POST request to accept the request
        response = self.client.post(reverse('handle_group_request', args=[str(self.request.id)]), {
            'action': 'accept'
        }, content_type='application/json')

        # Check that the response is a PermissionDenied error
        self.assertEqual(response.status_code, 403)

        # Check that user was not added to members
        self.assertFalse(self.user2 in self.group.members.all())

class GroupDeleteViewTest(BaseViewTest):
    def test_delete_group_success(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')

        # Send a POST request to delete the group
        response = self.client.post(reverse('delete_group', args=[self.group.id]))

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the group was deleted
        self.assertFalse(Group.objects.filter(pk=self.group.id).exists())

    def test_delete_group_failure(self):
        # Log in a different user (not the creator of the group)
        self.client.login(username='testuser2', password='testpassword2')

        # Send a POST request to delete the group
        response = self.client.post(reverse('delete_group', args=[self.group.id]))

        # Check if the response status code is 405 (Forbidden)
        self.assertEqual(response.status_code, 403)

        # Check if the group still exists
        self.assertTrue(Group.objects.filter(pk=self.group.id).exists())

    def test_delete_group_not_logged_in(self):
        # Send a POST request to delete the group without logging in
        response = self.client.post(reverse('delete_group', args=[self.group.id]))

        # Check if the response status code is 302 (Redirect to login)
        self.assertEqual(response.status_code, 302)

        # Check if the group still exists
        self.assertTrue(Group.objects.filter(pk=self.group.id).exists())

class GroupAddPhotoViewTest(BaseViewTest):
    def test_add_photo_authenticated_member(self):
        self.client.login(username='testuser', password='testpassword')
        uploaded_file = SimpleUploadedFile(
            'test_photo.jpg', b'file_content', content_type='image/jpeg'
        )
        response = self.client.post(reverse('add_group_photo', args=[str(self.group.id)]), data={'photo': uploaded_file})
        # Check that the response redirects to the group profile page
        self.assertRedirects(response, reverse('group_profile', args=[str(self.group.id)]))
        # Check that a photo object is created and associated with the group
        self.assertEqual(self.group.photos.count(), 1)
        photo = self.group.photos.all().first()
        self.assertEqual(photo.uploaded_by, self.user)
        self.assertEqual(photo.related_group, self.group)
        self.assertEqual(photo.photo.name, 'photos/test_photo.jpg')
        photo.delete()
        
    def test_add_photo_authenticated_non_member(self):
        # Log in as user who is not a member
        self.client.login(username='testuser2', password='testpassword2')
        self.uploaded_file = SimpleUploadedFile(
            'test_photo.jpg', b'file_content', content_type='image/jpeg'
        )
        response = self.client.post(reverse('add_group_photo', args=[str(self.group.id)]), data={'photo': self.uploaded_file})
        # Check that the response is a PermissionDenied error
        self.assertEqual(response.status_code, 403)
        # Check that no photo object is created
        self.assertFalse(Photo.objects.filter(related_group=self.group).exists())
        self.assertEqual(self.group.photos.count(), 0)

    def test_add_photo_unauthenticated(self):
        self.uploaded_file = SimpleUploadedFile(
            'test_photo.jpg', b'file_content', content_type='image/jpeg'
        )
        # Create a POST request to add a photo without logging in
        response = self.client.post(reverse('add_group_photo', args=[str(self.group.id)]), data={'photo': self.uploaded_file})
        
        # Assert that it redirects to the login page (status code 302)
        self.assertEqual(response.status_code, 302)
        
        # Check that no photo object is created
        self.assertFalse(Photo.objects.filter(related_group=self.group).exists())
        self.assertEqual(self.group.photos.count(), 0)

class GroupIsMemberViewTest(BaseViewTest):
    def test_is_member_authenticated_true(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('group_is_member', args=[str(self.group.id)]))
        self.assertEqual(response.status_code, 200)  # Expect a successful response
        data = response.json()
        self.assertTrue(data['is_member'])  # The user should be an member
    
    def test_is_member_authenticated_false(self):
        self.client.login(username='testuser2', password='testpassword2')
        response = self.client.get(reverse('group_is_member', args=[str(self.group.id)]))
        self.assertEqual(response.status_code, 200)  # Expect a successful response
        data = response.json()
        self.assertFalse(data['is_member'])  # The user should not be a member

    def test_is_member_unauthenticated(self):
        response = self.client.get(reverse('group_is_member', args=[str(self.group.id)]))
        self.assertEqual(response.status_code, 200)  # Expect a successful response
        data = response.json()
        self.assertFalse(data['is_member'])  # The user should not be a member

class GroupGetPhotosViewTest(BaseViewTest):
    def test_get_photos_with_photos(self):
        self.photo1 = Photo.objects.create(
            uploaded_by=self.user,
            photo=SimpleUploadedFile('photo1.jpg', b'photo_content', content_type='image/jpeg'),
            related_group = self.group
        )
        self.photo2 = Photo.objects.create(
            uploaded_by=self.user,
            photo=SimpleUploadedFile('photo2.jpg', b'photo_content', content_type='image/jpeg'),
            related_group = self.group
        )
        self.group.photos.add(self.photo1, self.photo2)

        response = self.client.get(reverse('get_group_photos', args=[str(self.group.id)]))
        self.assertEqual(response.status_code, 200)  # Expect a successful response
        data = response.json()
        self.assertIn('photos', data)  # Check if 'photos' key exists in the JSON response
        self.assertEqual(len(data['photos']), 2)  # Check if there are 2 photos in the response
        self.photo1.delete()
        self.photo2.delete()

    def test_get_photos_no_photos(self):
        response = self.client.get(reverse('get_group_photos', args=[str(self.group.id)]))
        self.assertEqual(response.status_code, 200)  # Expect a successful response
        data = response.json()
        self.assertIn('photos', data)  # Check if 'photos' key exists in the JSON response
        self.assertEqual(len(data['photos']), 0)  # Check if there are no photos in the response