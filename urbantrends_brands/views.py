from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import CreateBrandsFoundation, Module, BrandTier
from .serializers import (
    CreateBrandsFoundationSerializer,
    ModuleSerializer,
    BrandTierStandaloneSerializer,
)


class BrandFoundationViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides default CRUD actions for CreateBrandsFoundation.
    """
    queryset = CreateBrandsFoundation.objects.prefetch_related('modules', 'tiers').all()
    serializer_class = CreateBrandsFoundationSerializer


class ModuleViewSet(viewsets.ModelViewSet):
    """
    A viewset to manage the individual Module entries.
    """
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer


class BrandTierViewSet(viewsets.ModelViewSet):
    """
    Manage brand tiers. Filter by region, currency, tier level, or brand.
    """
    queryset = BrandTier.objects.select_related('brand').filter(is_active=True)
    serializer_class = BrandTierStandaloneSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['region', 'currency', 'tier', 'brand']
    ordering_fields = ['price', 'created_at']
    ordering = ['price']
