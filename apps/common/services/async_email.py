import threading
from apps.common.services.email_service import EmailService

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
