"""
Tests for the Django admin modification.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, Client


class AdminTests(TestCase):
    """Tests for admin."""

    def setUp(self):
        """Create user and client."""
        self.client = Client()
        self.User = get_user_model()
        self.superuser = self.User.objects.create_superuser(
            email='admin@example.com',
            password='test1234',
            name='admin user'
        )
        self.client.force_login(self.superuser)
        self.user = self.User.objects.create_user(
            email='user@example.com',
            password='test1234',
            name='user user'
        )

    def test_users_list(self):
        """Test that users are listed on page."""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test the edit user page works."""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.user.name)

    def test_create_user_page(self):
        """Test the create user page works."""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

        email = 'test@example.com'
        data = {
            'email': email,
            'password1': 'rf4<PmbLLgQPmrpt',
            'password2': 'rf4<PmbLLgQPmrpt',
            'name': 'test name'
        }
        res = self.client.post(url, data=data, follow=True)

        self.assertContains(res, email)
        self.assertTrue(self.User.objects.filter(email=email).exists())
