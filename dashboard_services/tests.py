from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model

from .views import DashboardProjectViewSet

User = get_user_model()


class DashboardProjectViewSetTest(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = MagicMock(spec=User)
        self.user.id = 1

    @patch("dashboard_services.views.DashboardProject.objects")
    def test_queryset_is_filtered_by_user(self, mock_objects):
        mock_qs = MagicMock()
        mock_objects.filter.return_value.order_by.return_value = mock_qs

        request = self.factory.get("/api/projects/")
        force_authenticate(request, user=self.user)

        view = DashboardProjectViewSet()
        view.request = request

        queryset = view.get_queryset()

        mock_objects.filter.assert_called_once_with(project_by=self.user)
        self.assertEqual(queryset, mock_qs)

    @patch("dashboard_services.views.DashboardProject.objects")
    def test_queryset_filters_by_status(self, mock_objects):
        mock_qs = MagicMock()
        mock_qs.filter.return_value = mock_qs
        mock_objects.filter.return_value.order_by.return_value = mock_qs

        request = self.factory.get("/api/projects/?status=published")
        force_authenticate(request, user=self.user)

        view = DashboardProjectViewSet()
        view.request = request

        view.get_queryset()

        mock_qs.filter.assert_called_with(project_status="published")

    def test_perform_create_sets_project_by_user(self):
        serializer = MagicMock()

        request = self.factory.post("/api/projects/")
        force_authenticate(request, user=self.user)

        view = DashboardProjectViewSet()
        view.request = request

        view.perform_create(serializer)

        serializer.save.assert_called_once_with(project_by=self.user)
