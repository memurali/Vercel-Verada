from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.utils.crypto import constant_time_compare

User = get_user_model()

class ChangePasswordTokenView(View):
    def get(self, request):
        email = request.GET.get("email")
        token = request.GET.get("token")
        return render(request, "users/change_password.html", {"email": email, "token": token})

    def post(self, request):
        email = request.POST.get("email")
        password1 = request.POST.get("new_password1")
        password2 = request.POST.get("new_password2")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "Invalid email."})

        if password1 != password2:
            return JsonResponse({"success": False, "message": "Passwords do not match."})
        if len(password1) < 8:
            return JsonResponse({"success": False, "message": "Password must be at least 8 characters."})

        user.set_password(password1)
        user.activation_token = None  # expire token
        user.save()
        return JsonResponse({"success": True})
