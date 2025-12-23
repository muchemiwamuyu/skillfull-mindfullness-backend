from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Service, ServiceTier


@receiver(post_save, sender=Service)
def create_default_service_tiers(sender, instance, created, **kwargs):
    if created:
        # Only create if tiers don't exist (double check)
        existing_tiers = instance.tiers.values_list('tier', flat=True)
        tiers_to_create = []

        for tier_name in ["basic", "standard", "premium"]:
            if tier_name not in existing_tiers:
                tiers_to_create.append(
                    ServiceTier(
                        service=instance,
                        tier=tier_name,
                        price=0,
                        features=f"{tier_name.capitalize()} features"
                    )
                )

        if tiers_to_create:
            ServiceTier.objects.bulk_create(tiers_to_create)
