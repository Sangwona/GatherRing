from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from group.models import Group, GroupRequest
from main.models import Interest
from group.forms import *

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
        self.assertRedirects(response, '/user/login/?next=/group/create/')

class BaseViewTest(TestCase):
    def setUp(self):
        # Create a user
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        
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

class ProfileGroupViewTest(BaseViewTest):
    def test_group_profile_view(self):
        # Make a GET request to the 'group' view with the group ID
        response = self.client.get(reverse('group_profile', args=[str(self.group.id)]))

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the rendered template contains the group's name
        self.assertContains(response, self.group.name)

        # Check if the rendered template contains the group's description
        self.assertContains(response, self.group.description)

class GroupEditTestCase(BaseViewTest):
    def test_edit_group_authenticated(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('edit_group', args=[str(self.group.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group/edit.html')
        self.assertIsInstance(response.context['form'], EditGroupForm)
    
    def test_edit_group_unauthenticated(self):
        # Attempt to access the create group page without authentication
        response = self.client.get(reverse('edit_group', args=[str(self.group.id)]))

        # Assert that it redirects to the login page (status code 302)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/user/login/?next=/group/edit/' + str(self.group.id) + '/')
        
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
        self.assertIsInstance(response.context['form'], EditGroupForm)

class GroupManageTestCase(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.group_request = GroupRequest.objects.create(
            group=self.group,
            user=self.user
        )
    
    def test_manage_view_with_invalid_group(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('manage_group', args=['9999']))
        
        # Returns a 404 page when the group is not found
        self.assertEqual(response.status_code, 404)

    def test_manage_group_authenticated(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('manage_group', args=[str(self.group.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group/manage.html')
        
        # Check if 'requests' is present in the context
        self.assertIn('requests', response.context)

        # Check the number of join requests in the context
        self.assertEqual(len(response.context['requests']), 1)  
    
    def test_manage_group_unauthenticated(self):
        # Attempt to access the create group page without authentication
        response = self.client.get(reverse('manage_group', args=[str(self.group.id)]))

        # Assert that it redirects to the login page (status code 302)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/user/login/?next=/group/manage/' + str(self.group.id) + '/')
    
    def test_manage_view_without_requests(self):
        empty_group = Group.objects.create(
            name='Empty Group',
            description='This group has no join requests.',
            location='Test Location',
            creator=self.user
        )

        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('manage_group', args=[str(empty_group.id)]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group/manage.html')
        
        # Assert that a message indicating no join requests is present
        self.assertContains(response, 'No requests.')

class AllGroupViewTest(TestCase):
    def setUp(self):
        # Create a user
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpassword")

        # Create groups
        self.group1 = Group.objects.create(
            name="Test Group",
            description="This is a test group",
            location="Test Location",
            visibility="Public",
            join_mode="Direct",
            capacity=50,
            creator=self.user,
        )

        self.group2 = Group.objects.create(
            name="Test Group2",
            description="This is a test group2",
            location="Test Location2",
            visibility="Public",
            join_mode="Direct",
            capacity=50,
            creator=self.user,
        )

    def test_all_view_with_groups(self):
        # Test when there are groups in the database
        response = self.client.get(reverse('all_groups'))

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'group/all.html')  

        # Check if groups are passed to the context
        self.assertQuerysetEqual(
            response.context['groups'],
            [self.group1, self.group2],
            ordered=False  # The order of groups doesn't matter
        )

    def test_all_view_without_groups(self):
        # Test when there are no groups in the database
        Group.objects.all().delete()  # Delete all groups
        response = self.client.get(reverse('all_groups'))

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'group/all.html')  

        # Check if an empty queryset is passed to the context
        self.assertQuerysetEqual(response.context['groups'], [])

class GroupViewsTestCase(BaseViewTest):
    def setUp(self):
        super().setUp()
        User = get_user_model()
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword2")

    def test_join_group_view(self):
        self.client.login(username='testuser2', password='testpassword2')

        # Initial state: User is not a member
        self.assertFalse(self.group.members.filter(pk=self.user2.pk).exists())

        # Sending a POST request to join the group
        self.client.post(reverse('join_group', args=[str(self.group.id)]))

        # After joining, the user should be a member
        self.assertTrue(self.group.members.filter(pk=self.user2.pk).exists())

        # Sending a second POST request to leave the group
        self.client.post(reverse('join_group', args=[str(self.group.id)]))

        # After leaving, the user should not be a member
        self.assertFalse(self.group.members.filter(pk=self.user2.pk).exists())
    
    def test_join_group_unauthenticated(self):
        # Attempt to join a group unauthenticated
        response = self.client.post(reverse('join_group', args=[str(self.group.id)]))

        # Assert that it redirects to the login page (status code 302)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/user/login/?next=/group/join/' + str(self.group.id) + '/')

    def test_create_group_request_view(self):
        self.client.login(username='testuser2', password='testpassword2')

        # Initial state: No group request exists
        self.assertFalse(self.group.requests.filter(user=self.user2).exists())

        # Sending a POST request to create a group request
        self.client.post(reverse('create_group_request', args=[str(self.group.id)]))

        # After creating the request, it should exist in the database
        self.assertTrue(self.group.requests.filter(user=self.user2).exists())

        # Sending a second POST request to cancel the request
        self.client.post(reverse('create_group_request', args=[str(self.group.id)]))

        # After canceling, the request should no longer exist
        self.assertFalse(self.group.requests.filter(user=self.user2).exists())

    def test_create_group_request_unauthenticated(self):
        # Attempt to join a group unauthenticated
        response = self.client.post(reverse('create_group_request', args=[str(self.group.id)]))

        # Assert that it redirects to the login page (status code 302)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/user/login/?next=/group/request/' + str(self.group.id) + '/')