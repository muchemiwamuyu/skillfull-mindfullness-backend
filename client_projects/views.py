from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .models import ClientProject
from .serializers import ClientProjectSerializer


class ClientProjectViewSet(ModelViewSet):
    serializer_class = ClientProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = ClientProject.objects.select_related("created_by")

        if not (user.is_staff or user.is_superuser):
            qs = qs.filter(created_by=user)

        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        scaffold_filter = self.request.query_params.get("scaffold_status")
        if scaffold_filter:
            qs = qs.filter(scaffold_status=scaffold_filter)

        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        project = self.get_object()
        if project.status != "pending":
            return Response(
                {"detail": f"Cannot approve a project with status '{project.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        project.status = "approved"
        project.save(update_fields=["status", "updated_at"])
        return Response({"detail": "Project approved."})

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        project = self.get_object()
        if project.status != "pending":
            return Response(
                {"detail": f"Cannot reject a project with status '{project.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        project.status = "rejected"
        project.save(update_fields=["status", "updated_at"])
        return Response({"detail": "Project rejected."})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def scaffold(self, request, pk=None):
        """Enqueue the repo scaffolding / analysis task for this project."""
        project = self.get_object()

        if not project.repo_url:
            return Response(
                {"detail": "No repository URL set on this project."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if project.scaffold_status in ("queued", "cloning", "analyzing"):
            return Response(
                {"detail": f"Scaffold already in progress (status: {project.scaffold_status})."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project.enqueue_scaffold()
        return Response({"detail": "Scaffold task enqueued.", "scaffold_status": "queued"})
