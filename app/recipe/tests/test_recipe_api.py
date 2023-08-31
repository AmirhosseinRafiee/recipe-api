"""
Test recipi APIs.
"""
from decimal import Decimal
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe
from ..serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')
User = get_user_model()


def create_recipe(user, **params):
    defaults = {
        'title': 'Sample recipe title',
        'description': 'Sample description',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'link': 'http://example.com/recipe.pdf'
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def get_detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=(recipe_id,))


class PublicRecipeAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.user = User.objects.create_user(
            'test@example.com',
            'testpass1234'
        )
        self.client = APIClient()

    def test_login_required(self):
        """Test retrieving recipes is login required."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = User.objects.create_user(
            'test@example.com',
            'testpass1234'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a  list of recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_for_user(self):
        """Test return list of recipes limited to authenticated user."""
        user2 = User.objects.create_user(
            'other@example.com',
            'otherpass1234'
        )
        create_recipe(user=user2)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        recipe = create_recipe(user=self.user)

        url = get_detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe."""
        payload = {
            'title': 'Sample title',
            'time_minutes': 20,
            'price': Decimal('5.99')
        }
        res = self.client.post(RECIPES_URL, data=payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)
