from django.test import TestCase
from user.models import User
from group.models import Group

class GroupTestCase(TestCase):
    def setUp(self):
        # Create a sample user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_group_creation(self):
        group = Group.objects.create(
            location='Sample Location',
            name='Sample Group',
            description='Sample Description',
            creator=self.user
        )
        
        # Check if the group is created successfully
        self.assertEqual(group.location, 'Sample Location')
        self.assertEqual(group.name, 'Sample Group')
        self.assertEqual(group.description, 'Sample Description')
        
        # Check if the creator is set correctly
        self.assertEqual(group.creator, self.user)        