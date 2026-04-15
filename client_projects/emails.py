from django.template.loader import render_to_string
from django.contrib.auth.models import User
from urbantrends_authentication.utils.emails import send_email


def send_project_submission_confirmation(project):
    """Send a submission confirmation email to the client."""
    user = project.created_by
    if not user or not user.email:
        return

    html_content = render_to_string(
        "emails/client_projects/project_confirmation.html",
        {"project": project, "user": user},
    )
    send_email(
        subject=f"We received your project — {project.project_name}",
        to_emails=[user.email],
        html_content=html_content,
    )


def send_new_project_alert(project):
    """Send a new project alert to all staff users."""
    staff_emails = list(
        User.objects.filter(is_staff=True, is_active=True)
        .exclude(email="")
        .values_list("email", flat=True)
    )
    if not staff_emails:
        return

    html_content = render_to_string(
        "emails/client_projects/new_project_alert.html",
        {"project": project},
    )
    send_email(
        subject=f"[New Client Project] #{project.id} — {project.project_name}",
        to_emails=staff_emails,
        html_content=html_content,
    )


def send_project_status_update(project):
    """Send a status update email (approved / rejected) to the client."""
    user = project.created_by
    if not user or not user.email:
        return

    html_content = render_to_string(
        "emails/client_projects/project_status_update.html",
        {
            "project": project,
            "user": user,
            "status_display": project.get_status_display(),
        },
    )
    send_email(
        subject=f"Your project '{project.project_name}' has been {project.get_status_display().lower()}",
        to_emails=[user.email],
        html_content=html_content,
    )
