from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ClientProjectViewSet

router = DefaultRouter()
router.register("projects", ClientProjectViewSet, basename="projects")

urlpatterns = router.urls
