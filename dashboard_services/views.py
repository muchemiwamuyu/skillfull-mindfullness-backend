from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from .models import DashboardProject, DashboardTeams, DashboardCustomProject
from .serializers import (
    DashboardProjectSerializer,
    DashboardTeamsSerializer,
    DashboardCustomProjectSerializer,
    DashboardCustomProjectStatusSerializer,
)
from .emails import (
    send_custom_project_confirmation,
    send_custom_project_status_update,
    send_new_custom_project_alert,
)


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

class DashboardCustomProjectViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "update_status":
            return DashboardCustomProjectStatusSerializer
        return DashboardCustomProjectSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return DashboardCustomProject.objects.all()
        return DashboardCustomProject.objects.filter(user=user)

    def perform_create(self, serializer):
        project = serializer.save(user=self.request.user)
        send_custom_project_confirmation(project)
        send_new_custom_project_alert(project)

    @action(detail=True, methods=["patch"], url_path="update-status", permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        """Staff endpoint to update project status and optionally add admin notes."""
        project = self.get_object()
        serializer = DashboardCustomProjectStatusSerializer(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        project.refresh_from_db()
        send_custom_project_status_update(project)
        return Response(DashboardCustomProjectSerializer(project).data)

    @action(detail=False, methods=["get"], url_path="analytics")
    def analytics(self, request):
        queryset = self.get_queryset()
        total = queryset.count()
        status_counts = {
            item["status"]: item["count"]
            for item in queryset.values("status").annotate(count=Count("id"))
        }
        return Response({"total": total, "by_status": status_counts})


class DashboardTeamsViewSet(ModelViewSet):
    serializer_class = DashboardTeamsSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.action in ("list", "retrieve"):
            queryset = DashboardTeams.objects.all().order_by("-created_at")
        else:
            queryset = DashboardTeams.objects.filter(added_by=self.request.user).order_by("-created_at")

        role = self.request.query_params.get("role")
        if role:
            queryset = queryset.filter(role=role)

        return queryset

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)
