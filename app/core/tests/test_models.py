"""
Tests for models.
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from .. import models


User = get_user_model()


def sample_user(email='sample@example.com', password='testpass1234'):
    """create a sample user."""
    return User.objects.create_user(email=email, password=password)


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass1234'
        user = User.objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test@EXAMPLE.com', 'test@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]
        for email, expected in sample_emails:
            user = User.objects.create_user(email, 'sample1234')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError"""
        with self.assertRaises(ValueError):
            User.objects.create_user('', 'sample1234')

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(
            'test@example.com',
            'sample1234'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        user = User.objects.create_user(
            'test@example.com',
            'testpass1234'
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description.'
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_teg_str(self):
        """Test the tag string representation."""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Test tag name',
        )

        self.assertEqual(str(tag), tag.name)
