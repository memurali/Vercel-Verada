from django.shortcuts import render
from apps.users.models import User, Role, UserRole

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@login_required(login_url='login') 
def role_form_view(request):
    return render(request, "users/roles-form.html")


@require_POST
def assign_role_ajax(request):
    role = request.POST.get("role")

    if not role:
        return JsonResponse({"success": False, "message": "All fields are required."})

    try:
        _ = Role.objects.get_or_create(name=role)
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})