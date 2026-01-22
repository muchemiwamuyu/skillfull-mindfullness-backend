from django.urls import path
from .views import hello, DevProjectView, DevProjectList
from rest_framework.routers import DefaultRouter

router = DefaultRouter()


# relevant urls
router.register("projects", DevProjectView, basename="projects")
router.register('all-projects', DevProjectList, basename='all-projects')

urlpatterns = router.urls