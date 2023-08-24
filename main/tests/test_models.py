import shutil
import tempfile
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from main.models import Interest, Photo

class InterestModelTest(TestCase):
    def test_interest_str_method(self):
        interest = Interest.objects.create(name="Hiking")

        # Check if the __str__ method returns the name of the interest
        self.assertEqual(str(interest), "Hiking")

    def test_interest_model_unique_name(self):
        # Create two interest instances with the same name (should raise IntegrityError)
        Interest.objects.create(name="Technology")
        with self.assertRaises(Exception):
            Interest.objects.create(name="Technology")

MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PhotoModelTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)  # delete the temp dir
        super().tearDownClass()

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="testpassword")

    def test_photo_str_method(self):        
        photo = Photo.objects.create(
            uploaded_by=self.user, 
            photo= SimpleUploadedFile('test.jpg', b'fakeContent')
        )
        
        # Ensure that the __str__ method returns the expected value
        self.assertEqual(str(photo), 'photos/test.jpg')