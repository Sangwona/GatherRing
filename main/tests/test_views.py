from django.test import TestCase
from django.urls import reverse

class IndexViewTest(TestCase):
    def test_index_view(self):
        # Make a GET request to the 'index' view
        response = self.client.get(reverse('index'))

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the response uses the 'main/index.html' template
        self.assertTemplateUsed(response, 'main/index.html')