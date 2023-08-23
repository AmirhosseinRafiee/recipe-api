"""
Test tag apis.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from ..serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')
User = get_user_model()


class PublicTagAPITest(TestCase):
    """Test the publicly available tags API."""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login required for retrieving tags."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITest(TestCase):
    """Test the authorized user tags API."""

    def setUp(self):
        self.user = User.objects.create_user(
            'test@example.com',
            'testpass1234'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags user authenticated."""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_for_user(self):
        """Test that tags returned are for the authenticated user."""
        user2 = User.objects.create_user(
            'other@example.com',
            'testpass1234'
        )
        Tag.objects.create(user=user2, name='Vegan')
        tag = Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_success(self):
        """Test creating a new tag."""
        payload = {
            'name': 'Vegan'
        }
        res = self.client.post(TAGS_URL, data=payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_blank(self):
        """Test creating a new tag with blank name."""
        payload = {
            'name': ''
        }
        res = self.client.post(TAGS_URL, data=payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
