from django.shortcuts import render
from apps.users.models import Role

from django.views.decorators.http import require_POST
from django.http import JsonResponse
from apps.users.models import Role, Permission, RolePermission, Module
from django.contrib.auth.decorators import login_required

from django.db import transaction

@login_required(login_url='login') 
def permission_form_view(request):
    modules = Module.objects.all()
    roles = Role.objects.all()
    return render(request, "users/permission-form.html", {"roles": roles, "modules": modules})


@require_POST
@transaction.atomic
def assign_permissions_ajax(request):
    role_id = request.POST.get("role_id")
    if not role_id:
        return JsonResponse({"success": False, "message": "Role is required."})

    try:
        role = Role.objects.get(id=role_id)
        RolePermission.objects.filter(role=role).delete()

        module_perms = {}

        # Step 1: Collect all perms by module
        for key in request.POST:
            if key == "role_id" or not key.endswith("[]"):
                continue

            module_code = key.rstrip("[]")
            perms = request.POST.getlist(key)

            if "no-access" in perms:
                continue

            if module_code not in module_perms:
                module_perms[module_code] = set()

            module_perms[module_code].update(perms)

        # Step 2: Create combined permission per module
        for module_code, perms in module_perms.items():
            try:
                module = Module.objects.get(code=module_code)
            except Module.DoesNotExist:
                continue

            can_read = "read" in perms
            can_write = "write" in perms
            can_delete = "delete" in perms

            permission, _ = Permission.objects.get_or_create(
                module=module,
                can_read=can_read,
                can_write=can_write,
                can_delete=can_delete,
                defaults={"description": f"Access for {module.name}"}
            )

                
            RolePermission.objects.create(role=role, permission=permission)

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


def get_role_permissions(request):
    role_id = request.GET.get("role_id")
    if not role_id:
        return JsonResponse({"success": False, "message": "Role ID required."}, status=400)

    try:
        role_permissions = RolePermission.objects.select_related('permission__module').filter(role_id=role_id)

        permission_map = {}
        for rp in role_permissions:
            module_code = rp.permission.module.code
            perms = []

            if rp.permission.can_read:
                perms.append("read")
            if rp.permission.can_write:
                perms.append("write")
            if rp.permission.can_delete:
                perms.append("delete")

            permission_map[module_code] = perms

        return JsonResponse({"success": True, "permissions": permission_map})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)