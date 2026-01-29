from django.db import models
from django.contrib.auth.models import User

class ClientProject(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    full_name = models.CharField(max_length=100)
    project_name = models.CharField(max_length=100)
    description = models.TextField()
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=20)
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
        editable=False, # optional, to prevent manual assignment
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project_name} ({self.status})"
