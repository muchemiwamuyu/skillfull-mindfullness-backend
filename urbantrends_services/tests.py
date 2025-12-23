from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

# Create your tests here.

class GreetingTest(APITestCase):
    def test_greetings(self):
        url = reverse("Greetings")

        response =  self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

