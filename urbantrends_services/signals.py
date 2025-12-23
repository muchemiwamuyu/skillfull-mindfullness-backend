from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Service, ServiceTier


@receiver(post_save, sender=Service)
def create_default_service_tiers(sender, instance, created, **kwargs):
    if created:
        ServiceTier.objects.bulk_create([
            ServiceTier(
                service=instance,
                tier="basic",
                price=0,
                features="Basic features"
            ),
            ServiceTier(
                service=instance,
                tier="standard",
                price=0,
                features="Standard features"
            ),
            ServiceTier(
                service=instance,
                tier="premium",
                price=0,
                features="Premium features"
            ),
        ])
