from django.test import TestCase
from django.contrib.auth import get_user_model
from user.forms import RegisterForm, LoginForm

class RegisterFormTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
    
    def test_register_form_valid(self):
        form = RegisterForm(data=self.user_data)
        self.assertTrue(form.is_valid())

    def test_register_form_invalid(self):
        invalid_data = self.user_data.copy()
        invalid_data['password2'] = 'differentpassword'
        form = RegisterForm(data=invalid_data)
        self.assertFalse(form.is_valid())

class LoginFormTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword123',
        }
        User = get_user_model()
        self.user = User.objects.create_user(**self.user_data)

    def test_login_form_valid(self):
        form = LoginForm(data=self.user_data)
        self.assertTrue(form.is_valid())

    def test_login_form_invalid(self):
        invalid_data = self.user_data.copy()
        invalid_data['password'] = 'incorrectpassword'
        form = LoginForm(data=invalid_data)
        self.assertFalse(form.is_valid())
