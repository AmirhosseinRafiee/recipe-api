"""
Test ingredient APIs.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient
from ..serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')
User = get_user_model()


class PublicIngredientAPITest(TestCase):
    """Test publicly available ingredients API."""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login required for retrieving ingredients."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITest(TestCase):
    """Test the authorized user ingredient API."""

    def setUp(self):
        self.user = User.objects.create_user(
            'test@example.com',
            'testpass1234'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients."""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_for_user(self):
        """Test that retrieving ingredients for authenticated user."""
        user2 = User.objects.create_user('other@example.com', 'testpass1234')
        Ingredient.objects.create(user=user2, name='Vinegar')
        ingredient = Ingredient.objects.create(user=self.user, name='Tumeric')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_success(self):
        """Test creating a new ingredient."""
        payload = {
            'name': 'Cabbage'
        }
        res = self.client.post(INGREDIENTS_URL, data=payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_ingredient_blank(self):
        """Test creating blank ingredient fails."""
        payload = {
            'name': ''
        }
        res = self.client.post(INGREDIENTS_URL, data=payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
