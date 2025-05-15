import random
from django.core.mail import send_mail
from .auth_service import AuthService
from apps.users.models import OTPRequest
from apps.common.services.async_email import AsyncEmailSender

def send_otp_email(user, otp_code):
    context = {
        "user": user,
        "otp": otp_code
    }

    AsyncEmailSender(
        subject="Your OTP Code - WasteFlow",
        to_email=user.email,
        template_name="emails/otp_email.html",
        context=context
    ).start()

class MFAService:

    @staticmethod
    def generate_otp(user):
        code = f"{random.randint(100000, 999999)}"
        otp = OTPRequest.objects.create(user=user, code=code)

        # Example: send via email
        print(f"Your OTP code is: {code}")
        send_otp_email(user, code)
        return otp.session_token

    @staticmethod
    def verify_otp(user, session_token, input_code):
        try:
            otp_obj = OTPRequest.objects.get(user=user, session_token=session_token, is_verified=False)
        except OTPRequest.DoesNotExist:
            return {"success": False, "error": "OTP session not found or already used."}

        if otp_obj.is_expired():
            return {"success": False, "error": "OTP has expired. Please login again."}

        if otp_obj.code != input_code:
            return {"success": False, "error": "The OTP you entered is incorrect."}

        otp_obj.is_verified = True
        otp_obj.save()
        return {"success": True}
