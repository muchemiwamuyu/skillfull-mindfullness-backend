from django.urls import path
from .views import hello, ServiceCategoryListView, ServiceDetailView

# relevant urls
urlpatterns = [
    path('greetings/', hello, name="Greetings"),
    path("services/", ServiceCategoryListView.as_view(), name="services"),
    path("services/<int:id>/", ServiceDetailView.as_view(), name="service details")
]