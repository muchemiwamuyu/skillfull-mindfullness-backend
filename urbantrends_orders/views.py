from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics
from .models import Order
from .serializers import OrderCreateSerializer, OrderSerializer
from rest_framework.permissions import IsAuthenticated

# Create your views here.
def hello(request):
    return HttpResponse("Hello from the orders app!")

class OrderCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class OrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")
