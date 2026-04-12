from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


def estimate_project_duration(project_type: str, complexity: str) -> str:
    """
    Estimate delivery time based on project type and complexity.
    Returns a human-readable range string.
    """
    project_type_lower = project_type.lower()

    base_days = {
        "landing page": 7,
        "portfolio": 7,
        "blog": 10,
        "e-commerce": 21,
        "ecommerce": 21,
        "shop": 21,
        "store": 21,
        "mobile app": 30,
        "mobile": 28,
        "dashboard": 14,
        "admin panel": 14,
        "crm": 21,
        "erp": 42,
        "api": 14,
        "backend": 14,
        "saas": 35,
        "marketplace": 35,
        "social": 28,
        "booking": 21,
        "management system": 21,
    }

    base = 14  # default
    for keyword, days in base_days.items():
        if keyword in project_type_lower:
            base = days
            break

    multipliers = {"simple": 0.75, "medium": 1.0, "complex": 1.5}
    factor = multipliers.get(complexity, 1.0)
    estimated = int(base * factor)

    # Round to nearest week boundary and express as a range
    low = max(3, estimated - 3)
    high = estimated + 5
    low_weeks = round(low / 7, 1)
    high_weeks = round(high / 7, 1)

    if high_weeks <= 1.5:
        return f"{low}–{high} days"
    return f"{low_weeks:.0f}–{high_weeks:.0f} weeks"


class DashboardCustomProject(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("reviewing", "Reviewing"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    COMPLEXITY_CHOICES = [
        ("simple", "Simple"),
        ("medium", "Medium"),
        ("complex", "Complex"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="custom_projects"
    )
    project_type = models.CharField(max_length=150)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    complexity = models.CharField(
        max_length=10, choices=COMPLEXITY_CHOICES, default="medium"
    )
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_currency = models.CharField(max_length=3, default="KES")

    # Computed at submission time
    estimated_duration = models.CharField(max_length=50, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    admin_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project_type} by {self.user} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.estimated_duration:
            self.estimated_duration = estimate_project_duration(
                self.project_type, self.complexity
            )
        super().save(*args, **kwargs)


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
    
class DashboardTeams(models.Model):
    ROLE_CHOICES = (
        ("developer", "Developer"),
        ("manager", "Manager"),
        ("testing", "Testing")
    )

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="testing"
    )
    image = models.ImageField(upload_to="team_images/", null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Dashboard_teams')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name

    



