from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardProject(models.Model):
    STATUS_CHOICES = (
        ("local", "Local"),
        ("published", "Published"),
    )

    project_name = models.CharField(max_length=100)
    project_description = models.TextField()
    project_category = models.CharField(max_length=255)
    project_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="local",
    )
    project_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Dashboard_projects')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project_name



