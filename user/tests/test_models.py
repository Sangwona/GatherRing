from django.test import TestCase
from user.models import User

class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword',
        }

    def test_user_str_method(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data['username'])
