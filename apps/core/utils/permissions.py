from apps.users.models import Permission
from apps.users.models import Module

def has_permission(user, module_code, action):
    """
    Check if user has a specific permission for a module.
    Always returns True for city_admin role.
    """
    # Grant full access to city_admin
    if user.user_role.filter(role__name__iexact="City Admin").exists():
        return True

    roles = user.user_role.values_list("role", flat=True)
    filter_args = {
        "rolepermission__role_id__in": roles,
        "module__code": module_code,
        f"can_{action}": True
    }
    return Permission.objects.filter(**filter_args).exists()


def get_user_module_permissions(user):
    if user.user_role.filter(role__name__iexact='City Admin').exists():
        modules = Module.objects.all()
        return {
            m.code: {"name": m.name, "read": True, "write": True, "delete": True}
            for m in modules
        }

    roles = user.user_role.values_list("role", flat=True)
    permissions = Permission.objects.filter(
        rolepermission__role_id__in=roles
    ).select_related('module')

    module_access = {}
    for perm in permissions:
        code = perm.module.code
        if code not in module_access:
            module_access[code] = {
                "name": perm.module.name,
                "read": False,
                "write": False,
                "delete": False,
            }
        module_access[code]["read"] |= perm.can_read
        module_access[code]["write"] |= perm.can_write
        module_access[code]["delete"] |= perm.can_delete

    print(f"module_access: {module_access}")

    return module_access