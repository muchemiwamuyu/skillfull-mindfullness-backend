from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  # or IsAdminUser for admin-only
from .models import Services
from .serializers import ServicesNestedSerializer

class ServicesViewSet(viewsets.ModelViewSet):
    """
    ViewSet to handle creation of service categories along with
    their items and tiers in a single POST request.
    """
    queryset = Services.objects.all()
    serializer_class = ServicesNestedSerializer
    permission_classes = [IsAuthenticated]  # change to IsAdminUser if needed

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
