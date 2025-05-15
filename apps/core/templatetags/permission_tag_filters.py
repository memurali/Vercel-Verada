from django import template
from apps.core.utils.permissions import has_permission

register = template.Library()

@register.filter(name='has_perm')
def has_perm(user, perm_str):
    try:
        module_code, action = perm_str.split(":")
        return has_permission(user, module_code, action)
    except:
        return False
