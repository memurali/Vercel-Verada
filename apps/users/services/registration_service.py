import secrets
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.urls import reverse
from apps.common.services.async_email import AsyncEmailSender
from apps.users.models import Role, UserRole
from django.db import transaction

User = get_user_model()

def send_welcome_email(user, password, activation_url, change_password_url):
    context = {
        "user": user,
        "password": password,
        "activation_url": activation_url,
        "change_password_url": change_password_url
    }

    AsyncEmailSender(
        subject="Welcome to Tracker System",
        to_email=user.email,
        template_name="emails/welcome_email.html",
        context=context
    ).start()


class RegistrationService:
    @staticmethod
    def register_user(name, email, phone, request):
        if User.objects.filter(email=email).exists():
            return False, "Email already registered."

        password = get_random_string(length=10)
        with transaction.atomic():
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name.split()[0],
                last_name=" ".join(name.split()[1:]) if len(name.split()) > 1 else "",
                phone=phone,
                is_active=False
            )

            role, _ = Role.objects.get_or_create(name='City Admin', restricted=True)
            _ = UserRole.objects.create(user=user,role=role)

            activation_token = secrets.token_urlsafe(32)
            user.activation_token = activation_token
            user.save()

        activation_url = request.build_absolute_uri(
            reverse("activate_account", args=[activation_token])
        )
        change_password_url = request.build_absolute_uri(
            reverse("change_password_token") + f"?email={user.email}&token={activation_token}"
        )

        subject = "Activate your account"
        message = f"""
Welcome {name},

Your temporary password is: {password}

To activate your account, click here:
{activation_url}

After activating, you can change your password here:
{change_password_url}

- Tracker System
"""
        print(message)
        send_welcome_email(user, password, activation_url, change_password_url)
        return True, None
