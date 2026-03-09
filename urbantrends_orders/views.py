from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Order
from .serializers import OrderCreateSerializer, OrderSerializer
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
