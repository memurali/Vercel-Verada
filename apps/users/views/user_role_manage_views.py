from django.shortcuts import render
from apps.users.models import User, Role, UserRole
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import transaction

@login_required(login_url='login') 
def user_roles_dashboard(request):
    query = request.GET.get("q", "").strip()
    users = User.objects.exclude(is_staff=True, is_superuser=True)

    if query:
        users = users.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )

    roles = Role.objects.all()
    user_roles = {
        ur.user_id: ur.role for ur in UserRole.objects.select_related("role")
    }

    for user in users:
        user.role = user_roles.get(user.id)

    return render(request, "users/dashboard-userroles.html", {
        "users": users,
        "roles": roles,
        "search_query": query
    })


@require_POST
@transaction.atomic
def update_user_role_ajax(request):
    user_id = request.POST.get("user_id")
    role_ids = request.POST.getlist("role_ids")

    if not user_id or not role_ids:
        return JsonResponse({"success": False, "message": "All fields are required."})

    try:
        user = User.objects.get(id=user_id)

        # Remove existing roles
        UserRole.objects.filter(user=user).delete()

        for role_id in role_ids:
            role = Role.objects.get(id=role_id)
            UserRole.objects.create(user=user, role=role)
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})