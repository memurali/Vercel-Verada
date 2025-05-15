from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from apps.users.models import UserRole, Role
from datetime import datetime

User = get_user_model()

@login_required(login_url='login') 
def edit_user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_role = UserRole.objects.filter(user=user).first()
    roles = Role.objects.all()
    return render(request, "users/editing-user-form.html", {"user": user, "roles": roles, "user_role":user_role})

@require_http_methods(["POST"])
def update_user_ajax(request):
    try:
        user_id = request.POST.get("user_id")
        user = get_object_or_404(User, id=user_id)

        user.first_name = request.POST.get("first_name", user.first_name).strip()
        user.last_name = request.POST.get("last_name", user.last_name).strip()
        user.email = request.POST.get("email", user.email).strip()
        user.phone = request.POST.get("phone", user.phone).strip()
        user.is_active = request.POST.get("status") == "active"

        role = Role.objects.get(id=request.POST.get("role"))
        UserRole.objects.update_or_create(
            user=user,
            defaults={'role': role}
        )

        if request.FILES.get("profile_pic"):
            user.profile_photo = request.FILES["profile_pic"]

        user.save()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})
