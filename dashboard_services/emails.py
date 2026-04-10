from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from urbantrends_authentication.utils.emails import send_email

User = get_user_model()


def send_custom_project_confirmation(project):
    user = project.user
    if not user or not user.email:
        return

    html_content = render_to_string(
        "emails/dashboard/custom_project_confirmation.html",
        {"project": project, "user": user},
    )
    send_email(
        subject=f"Project Request Received — {project.project_type} (est. {project.estimated_duration})",
        to_emails=[user.email],
        html_content=html_content,
    )


def send_custom_project_status_update(project):
    user = project.user
    if not user or not user.email:
        return

    html_content = render_to_string(
        "emails/dashboard/custom_project_status_update.html",
        {
            "project": project,
            "user": user,
            "status_display": project.get_status_display(),
        },
    )
    send_email(
        subject=f"Project Update — {project.project_type} is now {project.get_status_display()}",
        to_emails=[user.email],
        html_content=html_content,
    )


def send_new_custom_project_alert(project):
    """Alert all staff about a new custom project submission."""
    staff_emails = list(
        User.objects.filter(is_staff=True, is_active=True)
        .exclude(email="")
        .values_list("email", flat=True)
    )
    if not staff_emails:
        return

    html_content = render_to_string(
        "emails/dashboard/custom_project_confirmation.html",
        {"project": project, "user": project.user},
    )
    send_email(
        subject=f"[New Custom Project] #{project.id} — {project.project_type} by {project.user}",
        to_emails=staff_emails,
        html_content=html_content,
    )
