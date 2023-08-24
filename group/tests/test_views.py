from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from group.models import Group
from main.models import Interest
from user.models import User

class GroupViewTest(TestCase):
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

    def test_group_view(self):
        self.client.login(username='testuser', password='testpassword')

        # Make a GET request to the 'group' view with the group ID
        response = self.client.get(reverse('group', args=['1']))

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the rendered template contains the group's name
        self.assertContains(response, self.group.name)

        # Check if the rendered template contains the group's description
        self.assertContains(response, self.group.description)

class CreateGroupFormWizardTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.interest1 = Interest.objects.create(name='Interest 1')
        self.interest2 = Interest.objects.create(name='Interest 2')
    
    def test_group_creation(self):
        self.client.login(username='testuser', password='testpassword')

        location_data = {
            'create_group_form_wizard-current_step': '0', 
            '0-location': 'Test Location'}
        
        interests_data = {
            'create_group_form_wizard-current_step': '1', 
            '1-interests': [self.interest1.pk, self.interest2.pk]}
        
        name_data = {
            'create_group_form_wizard-current_step': '2', 
            '2-name': 'Test Group'}
        
        description_data = {
            'create_group_form_wizard-current_step': '3', 
            '3-description': 'Test Description'}
        
        response = self.client.post(reverse('create_group'), location_data)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('create_group'), interests_data)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('create_group'), name_data)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('create_group'), description_data)
        self.assertEqual(response.status_code, 302) # Expecting a redirect after last step
        self.assertEqual(response['Location'], reverse('group', args=['1']))  # Check the redirection URL
        
        # Check if the group was created
        self.assertEqual(Group.objects.count(), 1)
        group = Group.objects.first()
        self.assertEqual(group.location, location_data['0-location'])
        self.assertEqual(group.name, name_data['2-name'])
        self.assertEqual(group.description, description_data['3-description'])
        self.assertEqual(group.creator, self.user)
        self.assertEqual(list(group.interests.values_list('id', flat=True)), interests_data['1-interests'])

    def test_create_group_unauthenticated(self):
        # Attempt to access the create group page without authentication
        response = self.client.get(reverse('create_group'))

        # Assert that it redirects to the login page (status code 302)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/user/login?next=/group/create')