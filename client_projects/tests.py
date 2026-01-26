from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import ClientProject

class ClientProjectTests(APITestCase):

    def test_create_project_defaults_to_pending(self):
        url = reverse("projects-list")  # router name
        data = {
            "full_name": "John Doe",
            "project_name": "Website",
            "description": "Build a site",
            "email": "john@example.com",
            "phone": "+254712345678",
            "due_date": "2026-02-01"
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "pending")
