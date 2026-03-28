# urbantrends_orders/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, BrandOrder
from .emails import (
    send_order_confirmation,
    send_new_order_alert,
    send_brand_order_confirmation,
    send_brand_order_status_update,
    send_new_brand_order_alert,
)


@receiver(post_save, sender=Order)
def handle_order_saved(sender, instance, created, **kwargs):
    if created:
        send_order_confirmation(instance)
        send_new_order_alert(instance)


@receiver(post_save, sender=BrandOrder)
def handle_brand_order_saved(sender, instance, created, update_fields, **kwargs):
    if created:
        send_brand_order_confirmation(instance)
        send_new_brand_order_alert(instance)
    elif update_fields and "status" in update_fields:
        send_brand_order_status_update(instance)
