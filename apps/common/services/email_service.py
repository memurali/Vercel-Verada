from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

class EmailService:
    @staticmethod
    def send_email(subject, to_email, template_name, context=None, from_email=None, attachments=None):
        context = context or {}

        html_message = render_to_string(template_name, context)
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            to=[to_email]
        )
        email.content_subtype = 'html'  # Send as HTML email

        # Attachments if provided
        if attachments:
            for att in attachments:
                email.attach(att['filename'], att['content'], att['mimetype'])

        email.send()
