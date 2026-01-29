from rest_framework.routers import DefaultRouter
from .views import DashboardProjectViewSet

router = DefaultRouter()
router.register(r"projects", DashboardProjectViewSet, basename="projects")

urlpatterns = router.urls
