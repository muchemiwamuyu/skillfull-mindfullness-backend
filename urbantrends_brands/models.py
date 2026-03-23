from django.db import models


class Module(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CreateBrandsFoundation(models.Model):
    brand_name = models.CharField(max_length=100)
    brand_description = models.TextField()
    image = models.ImageField(upload_to='brand_images/')
    modules = models.ManyToManyField(Module)

    def __str__(self):
        return self.brand_name


CURRENCY_CHOICES = [
    ("USD", "US Dollar"),
    ("EUR", "Euro"),
    ("GBP", "British Pound"),
    ("KES", "Kenyan Shilling"),
    ("NGN", "Nigerian Naira"),
    ("ZAR", "South African Rand"),
    ("AUD", "Australian Dollar"),
    ("CAD", "Canadian Dollar"),
    ("JPY", "Japanese Yen"),
    ("INR", "Indian Rupee"),
    ("BRL", "Brazilian Real"),
    ("AED", "UAE Dirham"),
    ("SGD", "Singapore Dollar"),
    ("CHF", "Swiss Franc"),
    ("CNY", "Chinese Yuan"),
]

REGION_CHOICES = [
    ("africa", "Africa"),
    ("north_america", "North America"),
    ("south_america", "South America"),
    ("europe", "Europe"),
    ("asia", "Asia"),
    ("middle_east", "Middle East"),
    ("oceania", "Oceania"),
    ("global", "Global"),
]


class BrandTier(models.Model):
    TIER_CHOICES = [
        ("starter", "Starter"),
        ("growth", "Growth"),
        ("enterprise", "Enterprise"),
    ]

    brand = models.ForeignKey(
        CreateBrandsFoundation,
        on_delete=models.CASCADE,
        related_name="tiers"
    )
    tier = models.CharField(max_length=20, choices=TIER_CHOICES)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="USD")
    region = models.CharField(max_length=20, choices=REGION_CHOICES, default="global")
    features = models.JSONField(default=list, blank=True, help_text="List of features included in this tier")
    max_modules = models.PositiveIntegerField(default=0, help_text="Max modules allowed. 0 = unlimited")
    support_level = models.CharField(
        max_length=20,
        choices=[
            ("email", "Email Support"),
            ("priority", "Priority Support"),
            ("dedicated", "Dedicated Account Manager"),
        ],
        default="email"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["brand", "tier", "region"],
                name="unique_brand_tier_per_region"
            )
        ]
        ordering = ["brand", "price"]

    def __str__(self):
        return f"{self.brand.brand_name} - {self.get_tier_display()} ({self.get_region_display()}) - {self.currency} {self.price}"
