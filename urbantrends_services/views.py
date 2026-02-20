from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Services
from .serializers import ServicesNestedSerializer

class ServicesViewSet(viewsets.ModelViewSet):
    """
    - Public: list, retrieve
    - Protected: create, update, delete
    """
    queryset = Services.objects.all()
    serializer_class = ServicesNestedSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
