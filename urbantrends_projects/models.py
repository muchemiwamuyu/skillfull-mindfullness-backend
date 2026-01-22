from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class DevProject(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    live_link = models.URLField(blank=True, null=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="dev_projects"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["title", "created_by"],
                name="unique_project_per_user"
            )
        ]

    def __str__(self):
        return self.title

