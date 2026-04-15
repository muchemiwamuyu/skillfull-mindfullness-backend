from django.db import models
from django.contrib.auth.models import User


class ClientProject(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    SCAFFOLD_STATUS_CHOICES = [
        ("idle", "Idle"),
        ("queued", "Queued"),
        ("cloning", "Cloning"),
        ("analyzing", "Analyzing"),
        ("scaffolded", "Scaffolded"),
        ("failed", "Failed"),
    ]

    REPO_PROVIDER_CHOICES = [
        ("github", "GitHub"),
        ("gitlab", "GitLab"),
        ("bitbucket", "Bitbucket"),
    ]

    # --- Core fields ---
    project_name = models.CharField(max_length=100)
    description = models.TextField()
    email = models.EmailField(db_index=True)
    due_date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="client_projects",
        editable=False,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --- Repo fields ---
    repo_url = models.URLField(blank=True, null=True)
    repo_provider = models.CharField(max_length=20, choices=REPO_PROVIDER_CHOICES, blank=True, null=True)
    repo_branch = models.CharField(max_length=100, default="main", blank=True)
    repo_access_token = models.CharField(max_length=255, blank=True, null=True)

    # --- Scaffold output ---
    scaffold_status = models.CharField(
        max_length=20,
        choices=SCAFFOLD_STATUS_CHOICES,
        default="idle",
        db_index=True,
    )
    detected_stack = models.JSONField(blank=True, null=True)
    scaffold_output = models.JSONField(blank=True, null=True)
    scaffold_graph = models.JSONField(blank=True, null=True)
    scaffold_error = models.TextField(blank=True, null=True)
    scaffolded_at = models.DateTimeField(blank=True, null=True)

    # --- Analysis fields ---
    completeness_score = models.FloatField(blank=True, null=True)
    integrity_score = models.FloatField(blank=True, null=True)
    error_flags = models.JSONField(blank=True, null=True)
    suggestions = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.project_name} ({self.status}) [{self.scaffold_status}]"

    @property
    def is_scaffolded(self):
        return self.scaffold_status == "scaffolded"

    @property
    def repo_slug(self):
        if self.repo_url:
            parts = self.repo_url.rstrip("/").split("/")
            if len(parts) >= 2:
                return f"{parts[-2]}/{parts[-1]}"
        return None

    def enqueue_scaffold(self):
        """Mark as queued and dispatch the Celery task."""
        from .tasks import scaffold_project_task  # local import avoids circular import
        self.scaffold_status = "queued"
        self.scaffold_error = None
        self.save(update_fields=["scaffold_status", "scaffold_error", "updated_at"])
        scaffold_project_task.delay(self.pk)