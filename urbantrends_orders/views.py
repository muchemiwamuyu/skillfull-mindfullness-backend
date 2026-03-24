from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes as perm_classes
from .models import Order, BrandOrder
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    BrandOrderSerializer,
    BrandOrderCreateSerializer,
    BrandOrderStatusSerializer,
)
from rest_framework.permissions import IsAuthenticated

# Create your views here.
def hello(request):
    return HttpResponse("Hello from the orders app!")

class OrderCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        # Using the OrderSerializer for the response to include nested user info
        output_serializer = OrderSerializer(order, context={'request': request})
        return Response(output_serializer.data)


class OrderListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user

        # 1. Optimization: use select_related to fetch user info in 1 query
        queryset = Order.objects.select_related('user').all()

        # 2. Logic: Admins see everything, regular users see only their own
        if not user.is_staff:
            queryset = queryset.filter(user=user)

        return queryset.order_by("-created_at")


# Brand Order Views

class BrandOrderCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BrandOrderCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        output_serializer = BrandOrderSerializer(order, context={"request": request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class BrandOrderListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BrandOrderSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = BrandOrder.objects.select_related("user", "brand_tier__brand")

        if not user.is_staff:
            queryset = queryset.filter(user=user)

        # Optional filtering by status
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset


class BrandOrderDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BrandOrderSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = BrandOrder.objects.select_related("user", "brand_tier__brand")
        if not user.is_staff:
            queryset = queryset.filter(user=user)
        return queryset


class BrandOrderStatusUpdateView(generics.UpdateAPIView):
    """Staff-only endpoint to update brand order status."""
    permission_classes = [permissions.IsAdminUser]
    serializer_class = BrandOrderStatusSerializer

    def get_queryset(self):
        return BrandOrder.objects.select_related("user", "brand_tier__brand")

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order.status = serializer.validated_data["status"]
        order.save(update_fields=["status", "updated_at"])
        return Response(BrandOrderSerializer(order, context={"request": request}).data)
