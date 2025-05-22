from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.files.storage import FileSystemStorage
from apps.users.models import User, Role, UserRole
from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

import random
import string
import secrets
from django.urls import reverse
from django.utils.timezone import now
from django.db import transaction
from apps.audits.models import Official
from apps.common.services.email_service import EmailService
from apps.common.services.async_email import AsyncEmailSender

@login_required(login_url='login') 
def user_form_view(request):
    # In the future, you can pass roles/statuses from DB like:
    roles = Role.objects.all()
    statuses = ["active", "inactive"]

    context = {
        "page_title": "Add User",  # optional
        "roles": roles,
        "statuses": statuses,
    }
    return render(request, "users/user-form.html", context)

@require_POST
@transaction.atomic
def ajax_create_user(request):
    try:
        data = request.POST
        file = request.FILES.get("profile_picture")

        email = data.get("email").strip().lower()
        phone = data.get("phone").strip()

        if User.objects.filter(email=email).exists():
            return JsonResponse({"success": False, "message": "Email already exists"}, status=400)
        if User.objects.filter(phone=phone).exists():
            return JsonResponse({"success": False, "message": "Phone number already exists"}, status=400)
        
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

        role = Role.objects.get(id=data.get("role"))
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            phone=phone,
            is_active=(data.get("status") == "active")
        )

        user.profile_photo = file
        activation_token = secrets.token_urlsafe(32)
        user.activation_token = activation_token
        user.save()

        UserRole.objects.create(user=user, role=role)

        if role.name == "Auditor":
            Official.objects.create(
                user=user,
                name=data.get("first_name"),
                designation=role.name,
                created_user=request.user
            )

        print(f"Hi {user.first_name},\n\nYour account has been created.\n\nEmail: {email}\nPassword: {password}\n\nPlease login and change your password.")
        activation_url = request.build_absolute_uri(
            reverse("activate_account", args=[activation_token])
        )
        change_password_url = request.build_absolute_uri(
            reverse("change_password_token") + f"?email={user.email}&token={activation_token}"
        )
        context = {
            "user": user,
            "password": password,
            "activation_url": activation_url,
            "change_password_url": change_password_url,
            "user_role": role.name
        }

        EmailService.send_email(
            subject='Welcome to Tracker System',
            to_email=user.email,
            template_name='emails/add_user_email.html',
            context=context
        )

        # AsyncEmailSender(
        #     subject="Welcome to Tracker System",
        #     to_email=user.email,
        #     template_name="emails/add_user_email.html",
        #     context=context,
        # ).start()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)
