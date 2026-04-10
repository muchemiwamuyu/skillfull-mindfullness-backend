from rest_framework.routers import DefaultRouter
from .views import DashboardProjectViewSet, DashboardTeamsViewSet, DashboardCustomProjectViewSet

router = DefaultRouter()
router.register(r"projects", DashboardProjectViewSet, basename="projects")
router.register(r"custom-projects", DashboardCustomProjectViewSet, basename="custom-projects")
router.register(r"teams", DashboardTeamsViewSet, basename='Teams')

urlpatterns = router.urls
