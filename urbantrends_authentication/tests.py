from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

# Create your tests here.

class UserAndLoginTest(APITestCase):
    def test_create_and_login(self):
        # Create user
        create_url = reverse('Create urbantrends user')
        data = {
            "username": "client",
            "email": "client@gmail.com",
            "password": "Client@1234"
        }
        self.client.post(create_url, data, format='json')

        # Login user
        login_url = reverse('Login urbantrends user')
        login_data = {
            "username": "client",
            "password": "Client@1234"
        }
        response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

