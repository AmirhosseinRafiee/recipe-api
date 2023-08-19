"""
Test for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
User = get_user_model()


def create_user(**params):
    """Create and return a new user."""
    return User.objects.create_user(**params)


class PublicUserAPITest(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass1234',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, data=payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_create_user_with_email_exists_error(self):
        """Test error returned when creating a user with email exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass1234',
            'name': 'Test Name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, data=payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_short_password_error(self):
        """Test an error returned if password less than 5 chars."""
        payload = {
            'email': 'test@example.com',
            'password': 'pwpw',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, data=payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = User.objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
