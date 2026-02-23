from django.urls import path
from .views import hello, OrderCreateView, OrderListView

# relevant views
urlpatterns = [
    path("hello/", hello, name="orders_hello"),
    path("orders/", OrderListView.as_view(), name="order-list"),
    path("orders/create/", OrderCreateView.as_view(), name="order-create"),
]