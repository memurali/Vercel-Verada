import threading
from apps.common.services.email_service import EmailService
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


class AsyncEmailSender(threading.Thread):
    def __init__(self, subject, to_email, template_name, context):
        self.subject = subject
        self.to_email = to_email
        self.template_name = template_name
        self.context = context
        threading.Thread.__init__(self)

    def run(self):
        EmailService.send_email(
            subject=self.subject,
            to_email=self.to_email,
            template_name=self.template_name,
            context=self.context
        )

    # def run(self):
    #     message = render_to_string(self.template_name, self.context)
    #     email = EmailMessage(
    #         subject=self.subject,
    #         to=[self.to_email],
    #         body=message,
    #     )
    #     email.content_subtype = 'html'
    #     email.send()
