from django.shortcuts import render
from .serializers import DashboardProjectSerializer
from .models import DashboardProject
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

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

