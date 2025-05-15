from django.shortcuts import redirect

ROLE_ROUTE_MAP = {
    "data manager": "dashboard:data_manager",
    "auditor": "dashboard:auditor",
    "city admin": "dashboard:city_admin",
}

DEFAULT_DASHBOARD_ROUTE = "dashboard:dashboard_universal"

def redirect_user_based_on_role(user):
    user_roles = set(user.get_roles)
    matched_roles = user_roles & set(ROLE_ROUTE_MAP.keys())

    if matched_roles:
        role = next(iter(matched_roles))  # pick any one
        return redirect(ROLE_ROUTE_MAP[role])
    
    return redirect(DEFAULT_DASHBOARD_ROUTE)
