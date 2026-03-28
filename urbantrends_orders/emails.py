# urbantrends_orders/emails.py
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.conf import settings
from urbantrends_authentication.utils.emails import send_email


def send_order_confirmation(order):
    """Send order confirmation email to the customer."""
    user = order.user
    if not user or not user.email:
        return

    html_content = render_to_string(
        "emails/orders/order_confirmation.html",
        {"order": order, "user": user},
    )
    send_email(
        subject="Your Urbantrends Order is Confirmed",
        to_emails=[user.email],
        html_content=html_content,
    )


def send_order_status_update(order):
    """Send order status update email to the customer."""
    user = order.user
    if not user or not user.email:
        return

    # Order model doesn't have a status field — status lives on BrandOrder
    # This function is kept for future use if Order gains a status field.
    pass


def send_new_order_alert(order):
    """Send a new order alert email to all staff users."""
    staff_emails = list(
        User.objects.filter(is_staff=True, is_active=True)
        .exclude(email="")
        .values_list("email", flat=True)
    )
    if not staff_emails:
        return

    html_content = render_to_string(
        "emails/orders/new_order_alert.html",
        {"order": order},
    )
    send_email(
        subject=f"[New Order] #{order.id} — {order.service_name}",
        to_emails=staff_emails,
        html_content=html_content,
    )


def send_brand_order_confirmation(order):
    """Send brand order confirmation email to the customer."""
    user = order.user
    if not user or not user.email:
        return

    html_content = render_to_string(
        "emails/orders/brand_order_confirmation.html",
        {"order": order, "user": user},
    )
    send_email(
        subject=f"Your Brand Order for {order.brand_name} is Confirmed",
        to_emails=[user.email],
        html_content=html_content,
    )


def send_brand_order_status_update(order):
    """Send brand order status update email to the customer."""
    user = order.user
    if not user or not user.email:
        return

    html_content = render_to_string(
        "emails/orders/brand_order_status_update.html",
        {
            "order": order,
            "user": user,
            "status_display": order.get_status_display(),
        },
    )
    send_email(
        subject=f"Brand Order Update — {order.brand_name} is now {order.get_status_display()}",
        to_emails=[user.email],
        html_content=html_content,
    )


def send_new_brand_order_alert(order):
    """Send a new brand order alert email to all staff users."""
    staff_emails = list(
        User.objects.filter(is_staff=True, is_active=True)
        .exclude(email="")
        .values_list("email", flat=True)
    )
    if not staff_emails:
        return

    html_content = render_to_string(
        "emails/orders/new_order_alert.html",
        {"order": order},
    )
    send_email(
        subject=f"[New Brand Order] #{order.id} — {order.brand_name}",
        to_emails=staff_emails,
        html_content=html_content,
    )
