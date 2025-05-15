from django.shortcuts import render, redirect
from django.contrib import messages
from apps.users.forms.register_form import RegisterForm
from apps.users.services.registration_service import RegistrationService

from django.contrib.auth import login,logout
from apps.users.forms.login_form import LoginForm
from apps.users.forms.otp_form import OTPForm
from apps.users.services.auth_service import AuthService
from apps.users.services.mfa_service import MFAService

from apps.users.models import User
from django.http import JsonResponse

def register_view(request):
    form = RegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        try:
            _ = RegistrationService.register_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                password=form.cleaned_data['password']
            )
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')

    form = LoginForm(request.POST or None)
    return render(request, 'users/login.html', {'form': form})

def otp_verify_view(request):
    user_id = request.session.get("mfa_user_id")
    if not user_id:
        return JsonResponse({ "success": False, "message": "Session expired." })

    user = User.objects.get(id=user_id)
    if request.method == "POST":
        session_token = request.POST.get("session_token")
        code = request.POST.get("otp")

        if MFAService.verify_otp(user, session_token, code):
            login(request, user)
            del request.session["mfa_user_id"]
            return JsonResponse({ "success": True })
        else:
            return JsonResponse({ "success": False, "message": "Invalid or expired OTP." })

    return JsonResponse({ "success": False, "message": "Invalid request." })

def logout_view(request):
    logout(request)
    return redirect("login")  # or your custom login route