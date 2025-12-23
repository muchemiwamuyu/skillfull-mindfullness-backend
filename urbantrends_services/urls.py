from django.urls import path
from .views import hello, ServiceCategoryListView

# relevant urls
urlpatterns = [
    path('greetings/', hello, name="Greetings"),
    path("services/", ServiceCategoryListView.as_view(), name="services"),
]