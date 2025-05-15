from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from apps.users.forms.otp_form import OTPForm
from apps.users.models import User,OTPRequest
from apps.users.services.mfa_service import MFAService
from datetime import timedelta
import re

class OtpVerifyView(View):
    def get(self, request):
        user_id = request.session.get('mfa_user_id')
        if not user_id:
            messages.error(request, "Session expired. Please login again.")
            return redirect('users:login')

        otp_obj = OTPRequest.objects.filter(user_id=user_id, is_verified=False).latest("created_at")
        expires_at = otp_obj.created_at + timedelta(minutes=5)

        form = OTPForm(initial={"session_token": str(otp_obj.session_token)})

        return render(request, 'users/otp_verify.html', {         
            "form": form,
            "expires_at": expires_at.isoformat()
        })

    def post(self, request):
        form = OTPForm(request.POST)
        user_id = request.session.get("mfa_user_id")

        if not user_id:
            return JsonResponse({
                "success": False,
                "message": "Session expired. Please log in again."
            }, status=400)

        user = User.objects.get(id=user_id)

        if not form.is_valid():
            print(form.errors)
            return JsonResponse({
                "success": False,
                "message": "Invalid form submission. Please enter a valid 6-digit OTP."
            }, status=400)
        
        otp = form.cleaned_data.get('otp', '').strip()
        token = form.cleaned_data.get('session_token')

        if not re.fullmatch(r"\d{6}", otp):
            return JsonResponse({
                "success": False,
                "message": "OTP must be a 6-digit numeric code."
            }, status=400)
        
        result = MFAService.verify_otp(user, token, otp)

        if result["success"]:
            login(request, user)
            request.session.pop("mfa_user_id", None)
            return JsonResponse({"success": True, "redirect_url": "/dashboard"})

        return JsonResponse({
            "success": False,
            "message": result["error"]
        }, status=400)