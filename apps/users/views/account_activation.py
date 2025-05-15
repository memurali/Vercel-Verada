from django.views import View
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()

class ActivateAccountView(View):
    def get(self, request, token):
        try:
            user = User.objects.get(activation_token=token)
            user.is_active = True
            user.activation_token = None
            user.save()
            messages.success(request, "Account activated. Please log in.")
        except User.DoesNotExist:
            messages.error(request, "Invalid or expired activation token.")
        return redirect("login")
