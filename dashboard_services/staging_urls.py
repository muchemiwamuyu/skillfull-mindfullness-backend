from django.urls import path
from .views import StagingReposView

urlpatterns = [
    path("repos/", StagingReposView.as_view(), name="staging-repos"),
]
