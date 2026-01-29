from django.shortcuts import render
from rest_framework.permissions import AllowAny
from .models import ClientProject
from .serializers import ClientProjectSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

# Create your views here.

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ClientProject
from .serializers import ClientProjectSerializer


class ClientProjectViewSet(ModelViewSet):
    serializer_class = ClientProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Users only see THEIR projects.
        Admins see all projects.
        """
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return ClientProject.objects.all()

        return ClientProject.objects.filter(created_by=user)

    def perform_create(self, serializer):
        """
        Force project ownership on creation.
        Prevents spoofing via payload.
        """
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """
        Extra safety: ensure ownership on update.
        """
        serializer.save(created_by=self.request.user)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAdminUser],
    )
    def approve(self, request, pk=None):
        project = self.get_object()
        project.status = "approved"
        project.save(update_fields=["status"])
        return Response({"detail": "Project approved"})





