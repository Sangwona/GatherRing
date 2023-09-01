from django.test import TestCase
from ..forms import LocationForm1, InterestsForm2, NameForm3, DescriptionForm4
from main.models import Interest

class LocationForm1TestCase(TestCase):
    def test_location_form_valid_data(self):
        form = LocationForm1(data={'location': 'Sample Location'})
        self.assertTrue(form.is_valid())

    def test_location_form_empty_data(self):
        form = LocationForm1(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        
class InterestsForm2TestCase(TestCase):
    def setUp(self):
        # Create Interest objects
       self.interest1 = Interest.objects.create(name='Interest 1')
       self.interest2 = Interest.objects.create(name='Interest 2')

    def test_interests_form_valid_data(self):
        form = InterestsForm2(data={'interests': [self.interest1, self.interest2]})
        self.assertTrue(form.is_valid())

    def test_interests_form_empty_data(self):
        form = InterestsForm2(data={})
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)

class NameForm3TestCase(TestCase):
    def test_name_form_valid_data(self):
        form = NameForm3(data={'name': 'Sample Group'})
        self.assertTrue(form.is_valid())

    def test_name_form_empty_data(self):
        form = NameForm3(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)

class DescriptionForm4TestCase(TestCase):
    def test_description_form_valid_data(self):
        form = DescriptionForm4(data={'description': 'Sample Description'})
        self.assertTrue(form.is_valid())

    def test_description_form_empty_data(self):
        form = DescriptionForm4(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)