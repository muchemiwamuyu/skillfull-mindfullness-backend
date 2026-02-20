from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Services, ServiceItem, ServiceTier, Order, OrderItem
from .serializers import (
    ServicesSerializer,
    ServiceItemSerializer,
    ServiceTierSerializer,
    OrderSerializer,
    OrderItemSerializer
)
from django.contrib.auth.models import User


# ---------- Services / ServiceItems / Tiers ----------

class ServicesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List and retrieve all service categories with their services and tiers
    """
    queryset = Services.objects.prefetch_related('service_items__tiers').all()
    serializer_class = ServicesSerializer
    permission_classes = [permissions.AllowAny]


class ServiceItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceItem.objects.prefetch_related('tiers').all()
    serializer_class = ServiceItemSerializer
    permission_classes = [permissions.AllowAny]


class ServiceTierViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceTier.objects.select_related('service_item').all()
    serializer_class = ServiceTierSerializer
    permission_classes = [permissions.AllowAny]


# ---------- Orders / OrderItems ----------

class OrderViewSet(viewsets.ModelViewSet):
    """
    CRUD for orders. Nested order items are handled in the serializer.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own orders
        return Order.objects.filter(customer=self.request.user).prefetch_related('items__service_item', 'items__tier')

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    Optional: Manage order items separately (if needed)
    """
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return OrderItem.objects.filter(order__customer=self.request.user).select_related('service_item', 'tier', 'order')


# ---------- Admin Services CRUD ----------

class AdminServicesViewSet(viewsets.ModelViewSet):
    """
    Admin API to CRUD service categories, service items, and tiers
    """
    queryset = Services.objects.prefetch_related('service_items__tiers').all()
    serializer_class = ServicesSerializer
    permission_classes = [permissions.IsAdminUser]  # only admins

class AdminServiceItemViewSet(viewsets.ModelViewSet):
    queryset = ServiceItem.objects.prefetch_related('tiers').all()
    serializer_class = ServiceItemSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminServiceTierViewSet(viewsets.ModelViewSet):
    queryset = ServiceTier.objects.select_related('service_item').all()
    serializer_class = ServiceTierSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get('data'), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)


# ---------- Admin Orders View ----------

class AdminOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin can view all orders
    """
    queryset = Order.objects.prefetch_related('items__service_item', 'items__tier').all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]  # only admins