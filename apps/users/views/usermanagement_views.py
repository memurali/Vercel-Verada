from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.db.models import OuterRef, Subquery, Value, CharField, Case, When
from apps.users.models import UserRole, Role, User, Client
from django.db.models.functions import Concat
from django.conf import settings

from django.db.models import Q, F


# @login_required(login_url='login') 
# def dashboard_usermanagement_view(request):
#     search_query = request.GET.get('q', '').strip()

#     # Subquery to get the first role name for each user
#     first_role_subquery = Subquery(
#         UserRole.objects.filter(user=OuterRef('pk'))
#         .select_related('role')
#         .order_by('id')
#         .values('role__name')[:1]
#     )

#     # Base user queryset with annotations and select_related on client
#     base_users = User.objects.select_related('client').annotate(
#         role=first_role_subquery,
#         status=Case(
#             When(is_active=True, then=Value("Active")),
#             default=Value("Inactive"),
#             output_field=CharField()
#         ),
#         profile_photo_url=Case(
#             When(profile_photo__isnull=False, profile_photo__gt='', then=F('profile_photo')),
#             default=Value(''),
#             output_field=CharField()
#         )
#     ).exclude(is_staff=True, is_superuser=True)

#     # Apply search filters
#     if search_query:
#         base_users = base_users.filter(
#             Q(first_name__icontains=search_query) |
#             Q(last_name__icontains=search_query) |
#             Q(email__icontains=search_query) |
#             Q(phone__icontains=search_query) |
#             Q(role__icontains=search_query) |
#             Q(client__company_name__icontains=search_query)
#         )

#     # Extract desired fields for rendering
#     users = base_users.values(
#         'id',
#         'first_name',
#         'last_name',
#         'email',
#         'phone',
#         'status',
#         'date_joined',
#         'profile_photo_url',
#         'role',
#         'client_id',
#         'client__company_name',
#         'client__company_email',
#         'client__company_phone'
#     )

#     return render(request, "users/usermanagement.html", {
#         "users": users,
#         "search_query": search_query
#     })


@login_required(login_url='login') 
def dashboard_usermanagement_view(request):
    search_query = request.GET.get('q', '').strip()
    current_client_id = request.user.client_id  # 🔑 Get logged-in user's client ID

    # Subquery to get the first role name for each user
    first_role_subquery = Subquery(
        UserRole.objects.filter(user=OuterRef('pk'))
        .select_related('role')
        .order_by('id')
        .values('role__name')[:1]
    )

    # Base user queryset with annotations and select_related on client
    base_users = User.objects.select_related('client').annotate(
        role=first_role_subquery,
        status=Case(
            When(is_active=True, then=Value("Active")),
            default=Value("Inactive"),
            output_field=CharField()
        ),
        profile_photo_url=Case(
            When(profile_photo__isnull=False, profile_photo__gt='', then=F('profile_photo')),
            default=Value(''),
            output_field=CharField()
        )
    ).exclude(is_staff=True, is_superuser=True)

    # 🔒 Filter users by logged-in user's client
    if current_client_id:
        base_users = base_users.filter(client_id=current_client_id)
    else:
        base_users = base_users.none()  # no client assigned — show nothing


    # ❌ Exclude users with role = "City Admin"
    base_users = base_users.exclude(role="City Admin")

    # Apply search filters
    if search_query:
        base_users = base_users.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(role__icontains=search_query) |
            Q(client__company_name__icontains=search_query)
        )

    # Extract desired fields for rendering
    users = base_users.values(
        'id',
        'first_name',
        'last_name',
        'email',
        'phone',
        'status',
        'date_joined',
        'profile_photo_url',
        'role',
        'client_id',
        'client__company_name',
        'client__company_email',
        'client__company_phone'
    )

    return render(request, "users/usermanagement.html", {
        "users": users,
        "search_query": search_query
    })
