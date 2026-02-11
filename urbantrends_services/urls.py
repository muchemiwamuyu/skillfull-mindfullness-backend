from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    ServicesViewSet,
    ServiceItemViewSet,
    ServiceTierViewSet,
    OrderViewSet,
    OrderItemViewSet,
    AdminServicesViewSet,
    AdminServiceItemViewSet,
    AdminServiceTierViewSet,
    AdminOrderViewSet,
)

# ---------- Public / Read-only APIs ----------
public_router = DefaultRouter()
public_router.register(r'services', ServicesViewSet, basename='services')
public_router.register(r'service-items', ServiceItemViewSet, basename='service-items')
public_router.register(r'tiers', ServiceTierViewSet, basename='tiers')

# ---------- User APIs (authenticated) ----------
user_router = DefaultRouter()
user_router.register(r'orders', OrderViewSet, basename='orders')
user_router.register(r'order-items', OrderItemViewSet, basename='order-items')

# ---------- Admin APIs ----------
admin_router = DefaultRouter()
admin_router.register(r'services', AdminServicesViewSet, basename='admin-services')
admin_router.register(r'service-items', AdminServiceItemViewSet, basename='admin-service-items')
admin_router.register(r'tiers', AdminServiceTierViewSet, basename='admin-service-tiers')
admin_router.register(r'orders', AdminOrderViewSet, basename='admin-orders')

# ---------- URL Patterns ----------
urlpatterns = [
    # Public APIs
    path('api/', include(public_router.urls)),

    # Authenticated user APIs
    path('api/user/', include(user_router.urls)),

    # Admin APIs
    path('api/admin/', include(admin_router.urls)),
]
