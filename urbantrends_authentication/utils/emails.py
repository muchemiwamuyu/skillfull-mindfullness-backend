# utils/emails.py
from django.core.mail import EmailMessage
from django.conf import settings

def send_email(subject="Test Email", to_emails=None, html_content=None):
    try:
        email = EmailMessage(
            subject=subject,
            body=html_content or "",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to_emails or [],
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)
        return "sent"
    except Exception as e:
        print("Email sending error:", str(e))
        return str(e)
