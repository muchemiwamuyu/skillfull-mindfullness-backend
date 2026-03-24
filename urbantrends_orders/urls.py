from django.urls import path
from .views import (
    hello,
    OrderCreateView,
    OrderListView,
    BrandOrderCreateView,
    BrandOrderListView,
    BrandOrderDetailView,
    BrandOrderStatusUpdateView,
)

# relevant views
urlpatterns = [
    path("hello/", hello, name="orders_hello"),
    path("orders/", OrderListView.as_view(), name="order-list"),
    path("orders/create/", OrderCreateView.as_view(), name="order-create"),

    # Brand order tracking
    path("brand-orders/", BrandOrderListView.as_view(), name="brand-order-list"),
    path("brand-orders/create/", BrandOrderCreateView.as_view(), name="brand-order-create"),
    path("brand-orders/<int:pk>/", BrandOrderDetailView.as_view(), name="brand-order-detail"),
    path("brand-orders/<int:pk>/status/", BrandOrderStatusUpdateView.as_view(), name="brand-order-status"),
]