import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ClientProject
from .emails import (
    send_project_submission_confirmation,
    send_new_project_alert,
    send_project_status_update,
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ClientProject)
def handle_client_project_saved(sender, instance, created, update_fields, **kwargs):
    if created:
        try:
            send_project_submission_confirmation(instance)
        except Exception as e:
            logger.error("Failed to send project submission confirmation: %s", e)
        try:
            send_new_project_alert(instance)
        except Exception as e:
            logger.error("Failed to send new project staff alert: %s", e)
    elif update_fields and "status" in update_fields:
        try:
            send_project_status_update(instance)
        except Exception as e:
            logger.error("Failed to send project status update email: %s", e)
