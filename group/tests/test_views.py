from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from group.models import Group
from main.models import Interest
from user.models import User

class ProfileGroupViewTest(TestCase):
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

    def test_group_profile_view(self):
        self.client.login(username='testuser', password='testpassword')

        # Make a GET request to the 'group' view with the group ID
        response = self.client.get(reverse('group_profile', args=[str(self.group.id)]))

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
        self.assertRedirects(response, '/user/login?next=/group/create')

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