"""
Test ingredient APIs.
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient, Recipe
from ..serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')
User = get_user_model()


def create_recipe(user, **params):
    """Create and return recipe."""
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


def get_detail_url(ingredient_pk):
    """create and return an ingredient detail URL."""
    return reverse('recipe:ingredient-detail', args=(ingredient_pk,))


def create_user(email='test@example.com', password='testpass1234'):
    """Create and return user."""
    return User.objects.create_user(email=email, password=password)


class PublicIngredientAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving ingredients."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITest(TestCase):
    """Test the authorized user ingredient API."""

    def setUp(self):
        self.user = create_user()
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
        user2 = create_user(email='other@example.com')
        Ingredient.objects.create(user=user2, name='Vinegar')
        ingredient = Ingredient.objects.create(user=self.user, name='Tumeric')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """Test updating an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Cilantro')

        payload = {
            'name': 'Coriander'
        }
        url = get_detail_url(ingredient.pk)
        res = self.client.patch(url, data=payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Lettuce')

        url = get_detail_url(ingredient.pk)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assign_to_recipes(self):
        """Test listing ingredients, those assigned to recipes."""
        ingredient1 = Ingredient.objects.create(user=self.user, name='Apples')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Turkey')
        recipe = create_recipe(user=self.user, title='Apple Crumble')
        recipe.ingredients.add(ingredient1)

        params = {'assigned_only': True}
        res = self.client.get(INGREDIENTS_URL, data=params)

        s1 = IngredientSerializer(ingredient1)
        s2 = IngredientSerializer(ingredient2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filter_ingredients_unique(self):
        """Test filtered ingredients returns a unique list."""
        ingredient = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentils')
        recipe1 = create_recipe(user=self.user, title='Eggs Benedict')
        recipe2 = create_recipe(user=self.user, title='Herb Eggs')
        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)

        params = {'assigned_only': True}
        res = self.client.get(INGREDIENTS_URL, data=params)

        self.assertEqual(len(res.data), 1)
