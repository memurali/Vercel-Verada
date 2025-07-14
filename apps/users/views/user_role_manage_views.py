from django.shortcuts import render, get_object_or_404
from apps.users.models import User, Role, UserRole
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import transaction
from apps.audits.models import Official
import json


@login_required(login_url='login') 
def user_roles_dashboard(request):
    query = request.GET.get("q", "").strip()
    client_id = getattr(request.user, 'client_id', None)

    # 🔍 Get IDs of users with "City Admin" role
    city_admin_user_ids = UserRole.objects.filter(role__name="City Admin").values_list('user_id', flat=True)

    # users = User.objects.exclude(is_staff=True, is_superuser=True)
    users = User.objects.exclude(is_staff=True, is_superuser=True).exclude(id__in=city_admin_user_ids)

    if client_id:
        users = users.filter(client_id=client_id)
    else:
        users = users.none()  # No client assigned — return empty


    if query:
        users = users.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(client__company_name__icontains=query)

        )

    # roles = Role.objects.all()
    roles = Role.objects.exclude(name="City Admin")
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
            
            # if role.name == "Auditor":
            official_qs = Official.objects.filter(user=user)

            if official_qs.exists():
                # Update existing record
                official_qs.update(
                    name=user.first_name,
                    designation=role.name,
                    created_user=request.user
                )
            else:
                # Create new record
                Official.objects.create(
                    user=user,
                    name=user.first_name,
                    designation=role.name,
                    created_user=request.user
                )
            
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})
    


@login_required
def role_names_dashboard(request):
    Roles_obj = Role.objects.all()
    return render(request, "users/Roles-dashboard.html", {
        "Roles_obj":Roles_obj
    })



@login_required(login_url='login')
def edit_roles_view(request, id):
    Roles_id = id
    Roles = get_object_or_404(Role, id=Roles_id)
    return render(request, "users/edit-Roles-type.html", {
        "Roles": Roles,
    })


def update_roles_names(request, pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            role_name = data.get('role_name')

            Roles = get_object_or_404(Role, pk=pk)

            if Role.objects.filter(name=role_name).exclude(pk=pk).exists():
                return JsonResponse({'status': 'error', 'message': 'Another Roles with this name already exists.'})

            Roles.name = role_name
            Roles.save()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
