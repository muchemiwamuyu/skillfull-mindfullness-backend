from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ClientProject
from .emails import (
    send_project_submission_confirmation,
    send_new_project_alert,
    send_project_status_update,
)


@receiver(post_save, sender=ClientProject)
def handle_client_project_saved(sender, instance, created, update_fields, **kwargs):
    if created:
        send_project_submission_confirmation(instance)
        send_new_project_alert(instance)
    elif update_fields and "status" in update_fields:
        send_project_status_update(instance)
