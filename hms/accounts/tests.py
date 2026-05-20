from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class LogoutTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com',
            role='PATIENT'
        )

    def test_logout_get_request(self):
        # Log in the user
        login_success = self.client.login(username='testuser', password='testpassword123')
        self.assertTrue(login_success)

        # Send GET request to logout
        response = self.client.get(reverse('accounts:logout'))

        # Verify redirect to login page
        self.assertRedirects(response, reverse('accounts:login'))

        # Verify user is logged out (i.e. not in session anymore)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_post_request(self):
        # Log in the user
        login_success = self.client.login(username='testuser', password='testpassword123')
        self.assertTrue(login_success)

        # Send POST request to logout
        response = self.client.post(reverse('accounts:logout'))

        # Verify redirect to login page
        self.assertRedirects(response, reverse('accounts:login'))

        # Verify user is logged out (i.e. not in session anymore)
        self.assertNotIn('_auth_user_id', self.client.session)
