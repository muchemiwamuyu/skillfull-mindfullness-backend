from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from .models import DashboardProject, DashboardTeams
from .serializers import DashboardProjectSerializer, DashboardTeamsSerializer


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
        Project analytics:
        - total projects
        - counts by status
        - optional time range (?range=7d|30d)
        """
        queryset = self.get_queryset()

        range_filter = request.query_params.get("range")
        if range_filter == "7d":
            queryset = queryset.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            )
        elif range_filter == "30d":
            queryset = queryset.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            )

        total = queryset.count()

        status_counts = queryset.values("project_status").annotate(
            count=Count("id")
        )

        counts = {"local": 0, "published": 0}
        for item in status_counts:
            counts[item["project_status"]] = item["count"]

        percentages = {
            "local": round((counts["local"] / total) * 100, 2) if total else 0,
            "published": round((counts["published"] / total) * 100, 2) if total else 0,
        }

        return Response({
            "total_projects": total,
            "counts": counts,
            "percentages": percentages,
        })

class DashboardTeamsViewSet(ModelViewSet):
    serializer_class = DashboardTeamsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = DashboardTeams.objects.filter(added_by = self.request.user).order_by("-created_at")

        role = self.request.query_params.get("role")

        if role:
            queryset = queryset.filter(role=role)

        return queryset
    
    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)
