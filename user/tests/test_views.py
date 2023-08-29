from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from user.forms import EditUserForm

class BaseViewTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword123',
        }
        User = get_user_model()
        self.user = User.objects.create_user(**self.user_data)

class LoginViewTest(BaseViewTest):
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

class LogoutViewTest(BaseViewTest):
    def test_logout_view(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Should redirect after logout

class RegisterViewTest(BaseViewTest):
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
        self.assertContains(response, "The two password fields")
    
    def test_register_view_existing_username_POST(self):
        response = self.client.post(reverse('register'), {
            'username': self.user_data['username'],
            'password1': 'newpassword123',
            'password2': 'newpassword123',
        })
        self.assertEqual(response.status_code, 200)  # Should stay on the registration page
        self.assertTemplateUsed(response, 'user/register.html')
        self.assertContains(response, "A user with that username already exists.")

class UserProfileViewTest(BaseViewTest):
    def test_profile_view_with_existing_user(self):
        response = self.client.get(reverse('user_profile', args=[str(self.user.pk)]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/profile.html')
        self.assertEqual(response.context['profile_user'], self.user)

    def test_profile_view_with_nonexistent_user(self):
        non_existent_user_id = 9999
        response = self.client.get(reverse('user_profile', args=[str(non_existent_user_id)]))

        self.assertEqual(response.status_code, 404)

class EditViewTestCase(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.edit_url = reverse('edit_profile', args=[self.user.id])

    def test_edit_view_authenticated(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], EditUserForm)

    def test_edit_view_unauthenticated(self):
        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login') + f'?next={self.edit_url}')

    def test_edit_view_post_valid_data(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.post(self.edit_url, {
            'username': 'newusername',
            'photo': 'photo_url',
            'bio': 'New bio',
            'location': 'New location'
        })
        self.assertRedirects(response, reverse('user_profile', args=[self.user.id]))
