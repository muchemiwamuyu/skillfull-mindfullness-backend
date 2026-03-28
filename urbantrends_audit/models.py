from django.db import models
from django.contrib.auth.models import User


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        ("LOGIN", "Login"),
        ("LOGOUT", "Logout"),
        ("VIEW", "View"),
        ("APPROVE", "Approve"),
        ("REJECT", "Reject"),
        ("LIKE", "Like"),
        ("COMMENT", "Comment"),
        ("REGISTER", "Register"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    resource_type = models.CharField(max_length=100, db_index=True)
    resource_id = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    extra_data = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["action", "resource_type"]),
            models.Index(fields=["timestamp", "user"]),
        ]

    def __str__(self):
        user_label = self.user.username if self.user else "anonymous"
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {user_label} — {self.action} {self.resource_type} #{self.resource_id}"
