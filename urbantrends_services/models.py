from django.db import models
from django.core.exceptions import ValidationError


class ServiceCategories(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)

    def clean(self):
        if self.pk and self.services.count() < 5:
            raise ValidationError("Each category must have at least 5 services")

    def __str__(self):
        return self.title


class Service(models.Model):
    category = models.ForeignKey(
        ServiceCategories,
        related_name="services",
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    delivery_time = models.PositiveIntegerField(help_text="Delivery time in days")

    def __str__(self):
        return f"{self.name} ({self.category.title})"


class ServiceTier(models.Model):
    TIER_CHOICES = [
        ("basic", "Basic"),
        ("standard", "Standard"),
        ("premium", "Premium"),
    ]

    service = models.ForeignKey(
        Service,
        related_name="tiers",
        on_delete=models.CASCADE
    )
    tier = models.CharField(max_length=10, choices=TIER_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.TextField()

    class Meta:
        unique_together = ("service", "tier")  # no duplicate tiers

    def delete(self, *args, **kwargs):
        raise ValidationError("Service tiers cannot be deleted.")

    def __str__(self):
        return f"{self.service.name} - {self.tier}"
