from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.db.models import OuterRef, Subquery, Value, CharField, Case, When
from apps.users.models import UserRole, Role, User
from django.db.models.functions import Concat
from django.conf import settings

from django.db.models import Q

@login_required(login_url='login') 
def dashboard_usermanagement_view(request):
    search_query = request.GET.get('q', '').strip()

    first_role_subquery = Subquery(
        UserRole.objects.filter(user=OuterRef('pk'))
        .select_related('role')
        .order_by('id')
        .values('role__name')[:1]
    )

    base_users = User.objects.annotate(
        role=first_role_subquery,
        status=Case(
            When(is_active=True, then=Value("Active")),
            default=Value("Inactive"),
            output_field=CharField()
        ),
        profile_photo_url=Case(
            When(profile_photo__isnull=False, profile_photo__gt='', then=Concat(
                Value(settings.MEDIA_URL),
                'profile_photo',
                output_field=CharField()
            )),
            default=Value(''),
            output_field=CharField()
        )
    ).exclude(is_staff=True, is_superuser=True)

    if search_query:
        base_users = base_users.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(role__icontains=search_query)
        )

    users = base_users.values(
        'id', 'first_name', 'last_name', 'email', 'phone', 'status', 'date_joined', 'profile_photo_url', 'role'
    )

    return render(request, "users/usermanagement.html", {"users": users, "search_query": search_query})

