from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from .models import ClientProject


class ClientProjectTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testclient",
            email="client@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def _project_data(self, **overrides):
        data = {
            "project_name": "My Website",
            "description": "Build a responsive marketing site.",
            "email": "client@example.com",
            "due_date": "2027-01-01",
        }
        data.update(overrides)
        return data

    def test_create_project_defaults_to_pending(self):
        url = reverse("projects-list")
        response = self.client.post(url, self._project_data(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "pending")

    def test_scaffold_fields_are_read_only(self):
        """Clients cannot spoof scaffold fields."""
        url = reverse("projects-list")
        data = self._project_data()
        data["scaffold_status"] = "scaffolded"
        data["completeness_score"] = 1.0

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["scaffold_status"], "idle")
        self.assertIsNone(response.data["completeness_score"])

    def test_repo_access_token_is_write_only(self):
        """Access token must not appear in any response."""
        url = reverse("projects-list")
        data = self._project_data(
            repo_url="https://github.com/user/repo",
            repo_provider="github",
            repo_access_token="secret_token_abc",
        )

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("repo_access_token", response.data)

    def test_duplicate_submission_rejected(self):
        url = reverse("projects-list")
        self.client.post(url, self._project_data(), format="json")
        response = self.client.post(url, self._project_data(), format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_past_due_date_rejected(self):
        url = reverse("projects-list")
        response = self.client.post(
            url, self._project_data(due_date="2020-01-01"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_only_sees_own_projects(self):
        other_user = User.objects.create_user(username="other", password="pass")
        ClientProject.objects.create(
            project_name="Other Project",
            description="Other",
            email="other@example.com",
            due_date="2027-06-01",
            created_by=other_user,
        )
        ClientProject.objects.create(
            project_name="My Project",
            description="Mine",
            email="mine@example.com",
            due_date="2027-06-01",
            created_by=self.user,
        )

        url = reverse("projects-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["project_name"], "My Project")

    def test_approve_requires_staff(self):
        project = ClientProject.objects.create(
            project_name="Staff Test",
            description="Test",
            email="staff@example.com",
            due_date="2027-06-01",
            created_by=self.user,
        )
        url = reverse("projects-approve", kwargs={"pk": project.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_scaffold_action_requires_repo_url(self):
        project = ClientProject.objects.create(
            project_name="No Repo",
            description="Test",
            email="norepo@example.com",
            due_date="2027-06-01",
            created_by=self.user,
        )
        url = reverse("projects-scaffold", kwargs={"pk": project.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
