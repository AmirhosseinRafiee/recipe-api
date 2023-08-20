"""
Test for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_CREATE_URL = reverse('user:token-create')
TOKEN_DISCARD_URL = reverse('user:token-discard')
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

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        user_detail = {
            'email': 'test@example.com',
            'password': 'test-user-password1234',
            'name': 'Test Name'
        }
        create_user(**user_detail)

        payload = {
            'email': user_detail['email'],
            'password': user_detail['password']
        }
        res = self.client.post(TOKEN_CREATE_URL, data=payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credential(self):
        """Test returns error if credential invalid."""
        create_user(email='test@example.com', password='goodpass')

        payload = {'email': 'test@example.com', 'password': 'wrongpass'}
        res = self.client.post(TOKEN_CREATE_URL, data=payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test returns error if password is blank."""
        create_user(email='test@example.com', password='goodpass')

        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_CREATE_URL, data=payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_discard_token_error(self):
        """Test returns error if user isn't authenticated"""
        res = self.client.post(TOKEN_DISCARD_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITest(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass1234',
            name='Test Name'
        )
        self.client = APIClient()
        token, created = Token.objects.get_or_create(user=self.user)
        # self.client.force_authenticate(token=token)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_create_user_authenticated_error(self):
        """Test return error if user is already authenticated"""
        payload = {
            'email': 'test2@example.com',
            'password': 'testpass1234',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, data=payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(User.objects.filter(email=payload['email']).exists())

    def test_discard_token_success(self):
        """Test discarding token for logged in user."""
        res = self.client.post(TOKEN_DISCARD_URL)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Token.objects.filter(user=self.user).exists())
