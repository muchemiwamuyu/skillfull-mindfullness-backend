# urbantrends_audit/signals.py
#
# Central signal handlers for the audit log system.
# Connected in UrbantrendsAuditConfig.ready().
#
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.auth.models import User

from .utils import log_action


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _get_ip(request):
    if request is None:
        return None
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _get_ua(request):
    if request is None:
        return ""
    return request.META.get("HTTP_USER_AGENT", "")


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

@receiver(user_logged_in)
def handle_user_login(sender, request, user, **kwargs):
    log_action(
        action="LOGIN",
        resource_type="User",
        resource_id=user.pk,
        description=f"User '{user.username}' logged in.",
        user=user,
        ip_address=_get_ip(request),
        user_agent=_get_ua(request),
    )


@receiver(user_logged_out)
def handle_user_logout(sender, request, user, **kwargs):
    if user is None:
        return
    log_action(
        action="LOGOUT",
        resource_type="User",
        resource_id=user.pk,
        description=f"User '{user.username}' logged out.",
        user=user,
        ip_address=_get_ip(request),
        user_agent=_get_ua(request),
    )


@receiver(post_save, sender=User)
def handle_user_saved(sender, instance, created, **kwargs):
    if created:
        log_action(
            action="REGISTER",
            resource_type="User",
            resource_id=instance.pk,
            description=f"New user registered: '{instance.username}' ({instance.email}).",
            user=instance,
        )


# ---------------------------------------------------------------------------
# urbantrends_orders — Order & BrandOrder
# ---------------------------------------------------------------------------

def _connect_orders():
    from urbantrends_orders.models import Order, BrandOrder

    @receiver(post_save, sender=Order, weak=False)
    def handle_order_saved(sender, instance, created, **kwargs):
        action = "CREATE" if created else "UPDATE"
        description = (
            f"Order #{instance.id} created for service '{instance.service_name}' "
            f"(tier: {instance.tier_name}, price: {instance.price})."
            if created
            else f"Order #{instance.id} updated."
        )
        user = instance.user
        log_action(
            action=action,
            resource_type="Order",
            resource_id=instance.pk,
            description=description,
            user=user,
        )

    @receiver(post_delete, sender=Order, weak=False)
    def handle_order_deleted(sender, instance, **kwargs):
        log_action(
            action="DELETE",
            resource_type="Order",
            resource_id=instance.pk,
            description=f"Order #{instance.id} deleted (service: '{instance.service_name}').",
            user=instance.user,
        )

    @receiver(post_save, sender=BrandOrder, weak=False)
    def handle_brand_order_saved(sender, instance, created, update_fields, **kwargs):
        if created:
            log_action(
                action="CREATE",
                resource_type="BrandOrder",
                resource_id=instance.pk,
                description=(
                    f"Brand order #{instance.id} created for '{instance.brand_name}' "
                    f"(tier: {instance.tier_name}, status: {instance.status})."
                ),
                user=instance.user,
                extra_data={"status": instance.status, "price": str(instance.price)},
            )
        elif update_fields and "status" in update_fields:
            log_action(
                action="UPDATE",
                resource_type="BrandOrder",
                resource_id=instance.pk,
                description=f"Brand order #{instance.id} status updated to '{instance.get_status_display()}'.",
                user=instance.user,
                extra_data={"new_status": instance.status},
            )
        else:
            log_action(
                action="UPDATE",
                resource_type="BrandOrder",
                resource_id=instance.pk,
                description=f"Brand order #{instance.id} updated.",
                user=instance.user,
            )

    @receiver(post_delete, sender=BrandOrder, weak=False)
    def handle_brand_order_deleted(sender, instance, **kwargs):
        log_action(
            action="DELETE",
            resource_type="BrandOrder",
            resource_id=instance.pk,
            description=f"Brand order #{instance.id} deleted (brand: '{instance.brand_name}').",
            user=instance.user,
        )


# ---------------------------------------------------------------------------
# urbantrends_services — Services, ServiceItem, ServiceTier
# ---------------------------------------------------------------------------

def _connect_services():
    from urbantrends_services.models import Services, ServiceItem, ServiceTier

    @receiver(post_save, sender=Services, weak=False)
    def handle_service_saved(sender, instance, created, **kwargs):
        log_action(
            action="CREATE" if created else "UPDATE",
            resource_type="Services",
            resource_id=instance.pk,
            description=f"Service category '{instance.get_category_display()}' {'created' if created else 'updated'}.",
        )

    @receiver(post_delete, sender=Services, weak=False)
    def handle_service_deleted(sender, instance, **kwargs):
        log_action(
            action="DELETE",
            resource_type="Services",
            resource_id=instance.pk,
            description=f"Service category '{instance.get_category_display()}' deleted.",
        )

    @receiver(post_save, sender=ServiceItem, weak=False)
    def handle_service_item_saved(sender, instance, created, **kwargs):
        log_action(
            action="CREATE" if created else "UPDATE",
            resource_type="ServiceItem",
            resource_id=instance.pk,
            description=f"Service item '{instance.name}' {'created' if created else 'updated'}.",
        )

    @receiver(post_delete, sender=ServiceItem, weak=False)
    def handle_service_item_deleted(sender, instance, **kwargs):
        log_action(
            action="DELETE",
            resource_type="ServiceItem",
            resource_id=instance.pk,
            description=f"Service item '{instance.name}' deleted.",
        )

    @receiver(post_save, sender=ServiceTier, weak=False)
    def handle_service_tier_saved(sender, instance, created, **kwargs):
        log_action(
            action="CREATE" if created else "UPDATE",
            resource_type="ServiceTier",
            resource_id=instance.pk,
            description=f"Service tier '{instance}' {'created' if created else 'updated'}.",
        )

    @receiver(post_delete, sender=ServiceTier, weak=False)
    def handle_service_tier_deleted(sender, instance, **kwargs):
        log_action(
            action="DELETE",
            resource_type="ServiceTier",
            resource_id=instance.pk,
            description=f"Service tier '{instance}' deleted.",
        )


# ---------------------------------------------------------------------------
# urbantrends_blogs — BlogPost, Comment, Like
# ---------------------------------------------------------------------------

def _connect_blogs():
    from urbantrends_blogs.models import BlogPost, Comment, Like

    @receiver(post_save, sender=BlogPost, weak=False)
    def handle_blog_post_saved(sender, instance, created, **kwargs):
        log_action(
            action="CREATE" if created else "UPDATE",
            resource_type="BlogPost",
            resource_id=instance.pk,
            description=f"Blog post '{instance.title}' {'created' if created else 'updated'} by '{instance.user}'.",
            user=instance.user,
        )

    @receiver(post_delete, sender=BlogPost, weak=False)
    def handle_blog_post_deleted(sender, instance, **kwargs):
        log_action(
            action="DELETE",
            resource_type="BlogPost",
            resource_id=instance.pk,
            description=f"Blog post '{instance.title}' deleted.",
            user=instance.user,
        )

    @receiver(post_save, sender=Comment, weak=False)
    def handle_comment_saved(sender, instance, created, **kwargs):
        if created:
            log_action(
                action="COMMENT",
                resource_type="Comment",
                resource_id=instance.pk,
                description=f"User '{instance.user}' commented on post '{instance.post}'.",
                user=instance.user,
            )

    @receiver(post_delete, sender=Comment, weak=False)
    def handle_comment_deleted(sender, instance, **kwargs):
        log_action(
            action="DELETE",
            resource_type="Comment",
            resource_id=instance.pk,
            description=f"Comment #{instance.id} on post '{instance.post}' deleted.",
            user=instance.user,
        )

    @receiver(post_save, sender=Like, weak=False)
    def handle_like_saved(sender, instance, created, **kwargs):
        if created:
            log_action(
                action="LIKE",
                resource_type="Like",
                resource_id=instance.pk,
                description=f"User '{instance.user}' liked post '{instance.post}'.",
                user=instance.user,
            )

    @receiver(post_delete, sender=Like, weak=False)
    def handle_like_deleted(sender, instance, **kwargs):
        log_action(
            action="DELETE",
            resource_type="Like",
            resource_id=instance.pk,
            description=f"User '{instance.user}' unliked post '{instance.post}'.",
            user=instance.user,
        )


# ---------------------------------------------------------------------------
# urbantrends_projects — DevProject
# ---------------------------------------------------------------------------

def _connect_projects():
    from urbantrends_projects.models import DevProject

    @receiver(post_save, sender=DevProject, weak=False)
    def handle_dev_project_saved(sender, instance, created, **kwargs):
        log_action(
            action="CREATE" if created else "UPDATE",
            resource_type="DevProject",
            resource_id=instance.pk,
            description=f"Dev project '{instance.title}' {'created' if created else 'updated'} by '{instance.created_by}'.",
            user=instance.created_by,
        )

    @receiver(post_delete, sender=DevProject, weak=False)
    def handle_dev_project_deleted(sender, instance, **kwargs):
        log_action(
            action="DELETE",
            resource_type="DevProject",
            resource_id=instance.pk,
            description=f"Dev project '{instance.title}' deleted.",
            user=instance.created_by,
        )


# ---------------------------------------------------------------------------
# client_projects — ClientProject
# ---------------------------------------------------------------------------

def _connect_client_projects():
    from client_projects.models import ClientProject

    @receiver(post_save, sender=ClientProject, weak=False)
    def handle_client_project_saved(sender, instance, created, update_fields, **kwargs):
        if created:
            log_action(
                action="CREATE",
                resource_type="ClientProject",
                resource_id=instance.pk,
                description=(
                    f"Client project '{instance.project_name}' submitted by "
                    f"'{instance.full_name}' ({instance.email})."
                ),
                user=instance.created_by,
                extra_data={"status": instance.status},
            )
        elif update_fields and "status" in update_fields:
            action = "APPROVE" if instance.status == "approved" else (
                "REJECT" if instance.status == "rejected" else "UPDATE"
            )
            log_action(
                action=action,
                resource_type="ClientProject",
                resource_id=instance.pk,
                description=f"Client project '{instance.project_name}' status changed to '{instance.get_status_display()}'.",
                user=instance.created_by,
                extra_data={"new_status": instance.status},
            )
        else:
            log_action(
                action="UPDATE",
                resource_type="ClientProject",
                resource_id=instance.pk,
                description=f"Client project '{instance.project_name}' updated.",
                user=instance.created_by,
            )

    @receiver(post_delete, sender=ClientProject, weak=False)
    def handle_client_project_deleted(sender, instance, **kwargs):
        log_action(
            action="DELETE",
            resource_type="ClientProject",
            resource_id=instance.pk,
            description=f"Client project '{instance.project_name}' deleted.",
            user=instance.created_by,
        )


# ---------------------------------------------------------------------------
# urbantrends_brands — CreateBrandsFoundation, BrandTier
# ---------------------------------------------------------------------------

def _connect_brands():
    from urbantrends_brands.models import CreateBrandsFoundation, BrandTier

    @receiver(post_save, sender=CreateBrandsFoundation, weak=False)
    def handle_brand_saved(sender, instance, created, **kwargs):
        log_action(
            action="CREATE" if created else "UPDATE",
            resource_type="Brand",
            resource_id=instance.pk,
            description=f"Brand '{instance.brand_name}' {'created' if created else 'updated'}.",
        )

    @receiver(post_delete, sender=CreateBrandsFoundation, weak=False)
    def handle_brand_deleted(sender, instance, **kwargs):
        log_action(
            action="DELETE",
            resource_type="Brand",
            resource_id=instance.pk,
            description=f"Brand '{instance.brand_name}' deleted.",
        )

    @receiver(post_save, sender=BrandTier, weak=False)
    def handle_brand_tier_saved(sender, instance, created, **kwargs):
        log_action(
            action="CREATE" if created else "UPDATE",
            resource_type="BrandTier",
            resource_id=instance.pk,
            description=f"Brand tier '{instance}' {'created' if created else 'updated'}.",
        )

    @receiver(post_delete, sender=BrandTier, weak=False)
    def handle_brand_tier_deleted(sender, instance, **kwargs):
        log_action(
            action="DELETE",
            resource_type="BrandTier",
            resource_id=instance.pk,
            description=f"Brand tier '{instance}' deleted.",
        )


# ---------------------------------------------------------------------------
# Wire everything up (called from apps.py ready())
# ---------------------------------------------------------------------------

def connect_all_signals():
    _connect_orders()
    _connect_services()
    _connect_blogs()
    _connect_projects()
    _connect_client_projects()
    _connect_brands()
