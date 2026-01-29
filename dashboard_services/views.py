from django.shortcuts import render
from .serializers import DashboardProjectSerializer
from .models import DashboardProject
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count

# Create your views here.
class DashboardProjectViewSet(ModelViewSet):
    serializer_class = DashboardProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = DashboardProject.objects.filter(
            project_by=self.request.user
        ).order_by("-created_at")

        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(project_status=status)
        return queryset

    def perform_create(self, serializer):
        serializer.save(project_by=self.request.user)

    @action(detail=False, methods=["get"], url_path="analytics")
    def analytics(self, request):
        """
        Returns analytics for the authenticated user's projects:
        - total projects
        - count by status (local / published)
        """
        queryset = self.get_queryset()

        # Aggregate counts by status
        status_counts = queryset.values("project_status").annotate(count=Count("id"))

        # Build a simple dict with 0 defaults for statuses not present
        analytics_data = {"local": 0, "published": 0}
        for item in status_counts:
            analytics_data[item["project_status"]] = item["count"]

        return Response({
            "total_projects": queryset.count(),
            "by_status": analytics_data
        })

