from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

default_service_item_id = 1

class Services(models.Model):
    CATEGORIES_CHOICES = [
        ("software-development", "Software Development"),
        ("web-digital-solutions", "Web & Digital Solutions"),
        ("cloud-infrastructure", "Cloud Infrastructure"),
        ("ui/ux-product-design", "UI/UX Product Design"),
        ("maintenance-support", "Maintenance & Support"),
        ("consulting-strategy", "Consulting & Strategy"),
    ]
    
    category = models.CharField(max_length=50, choices=CATEGORIES_CHOICES)

    def __str__(self):
        return self.get_category_display()


class ServiceItem(models.Model):
    services_category = models.ForeignKey(
        Services, 
        on_delete=models.CASCADE, 
        related_name="service_items"
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.services_category.get_category_display()})"


class ServiceTier(models.Model):
    service_item = models.ForeignKey(
        ServiceItem,
        on_delete=models.CASCADE,
        related_name="tiers"
    )

    TIER_CHOICES = [
        ("basic", "Basic"),
        ("standard", "Standard"),
        ("premium", "Premium"),
    ]

    tier = models.CharField(max_length=10, choices=TIER_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["service_item", "tier"],
                name="unique_service_tier_per_item"
            )
        ]

    def __str__(self):
        return f"{self.service_item.name} - {self.get_tier_display()}"



class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_price(self):
        # sum of all items in this order
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    service_item = models.ForeignKey(ServiceItem, on_delete=models.CASCADE)
    tier = models.ForeignKey(ServiceTier, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def clean(self):
        # Ensure the tier belongs to the selected service
        if self.tier.service_item != self.service_item:
            raise ValidationError("Selected tier does not belong to the selected service.")

    def total_price(self):
        return (self.tier.price or 0) * self.quantity

    def __str__(self):
        return f"{self.service_item.name} ({self.tier.get_tier_display()}) x{self.quantity}"
