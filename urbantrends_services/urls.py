from django.urls import path
from .views import hello, ServiceCategoryListView, ServiceDetailView, CreateServicesView

# relevant urls
urlpatterns = [
    path('greetings/', hello, name="Greetings"),
    path("services/", ServiceCategoryListView.as_view(), name="services"),
    path("services/<int:id>/", ServiceDetailView.as_view(), name="service details"),
    path("services/create/", CreateServicesView.as_view(), name="create service"),
]