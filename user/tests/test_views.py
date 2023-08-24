from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class UserViewsTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword123',
        }
        User = get_user_model()
        self.user = User.objects.create_user(**self.user_data)
    
    def test_login_view_GET(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/login.html')

    def test_login_view_valid_POST(self):
        response = self.client.post(reverse('login'), self.user_data)
        self.assertEqual(response.status_code, 302)  # Should redirect after successful login
    
    def test_login_view_invalid_POST(self):
        invalid_data = self.user_data.copy()
        invalid_data['password'] = 'wrongpassword'
        response = self.client.post(reverse('login'), invalid_data)
        self.assertEqual(response.status_code, 200)  # Should stay on the login page
        self.assertTemplateUsed(response, 'user/login.html')
        self.assertContains(response, "Please enter a correct username and password. Note that both fields may be case-sensitive.")

    def test_logout_view(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Should redirect after logout

    def test_register_view_GET(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/register.html')

    def test_register_view_valid_POST(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful registration

    def test_register_view_invalid_POST(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'newpassword123',
            'password2': 'differentpassword',
        })
        self.assertEqual(response.status_code, 200)  # Should stay on the registration page
        self.assertTemplateUsed(response, 'user/register.html')
        self.assertContains(response, "The two password fields didn’t match.")
        