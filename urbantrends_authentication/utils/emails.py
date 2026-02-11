import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from django.conf import settings


def send_email():
    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails="edwinwamuyu199@gmail.com",
        subject="This is jest testing",
        html_content="<Strong>Hello from noreply@urbantrends.dev!</strong>",
    )

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        print("SendGrid error:", str(e))
        return None
