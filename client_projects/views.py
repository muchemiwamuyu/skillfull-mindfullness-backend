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

class ClientProjectViewSet(ModelViewSet):
    serializer_class = ClientProjectSerializer
    queryset = ClientProject.objects.all()

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




