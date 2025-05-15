from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.common.utils.redirects import redirect_user_based_on_role
from apps.common.utils.decorators import role_required
from apps.waste_generators.models import WasteSource
from apps.core.models import CommodityGroup

from django.db.models import Sum
from django.utils.timezone import now
from datetime import timedelta, date
from django.db.models import Sum

@login_required(login_url='login')
def dashboard_view(request):
    return redirect_user_based_on_role(request.user)

def dashboard_analytics():
    today = now().date()

    # Helper functions
    def _get_weight_and_last_update_by_group(group_name):
        qs = WasteSource.objects.filter(waste_type__name__iexact=group_name)
        waste_weight = qs.aggregate(waste_weight=Sum('waste_weight'))['waste_weight'] or 0
        last_record = qs.order_by('-created_at').first()
        last_updated = last_record.created_at.strftime("%d/%m/%Y") if last_record else None
        return waste_weight, last_updated

    def _get_month_weight_by_group(group_name, year, month):
        return WasteSource.objects.filter(
            waste_type__name__iexact=group_name,
            created_at__year=year,
            created_at__month=month
        ).aggregate(waste_weight=Sum('waste_weight'))['waste_weight'] or 0
    
    current_month = today.month
    current_year = today.year

    previous_month = current_month - 1
    previous_year = current_year
    if previous_month == 0:
        previous_month = 12
        previous_year -= 1

    stats = {}
    categories = {
        'food_waste': 'Food Recovery',
        'recycle': 'Total Waste Recovered',
        'compost': 'Compost',
        'landfill': 'Total Trash Weight'
    }

    for group_name, display_name in categories.items():
        total, last_updated = _get_weight_and_last_update_by_group(group_name)

        current_month_total = _get_month_weight_by_group(group_name, current_year, current_month)
        previous_month_total = _get_month_weight_by_group(group_name, previous_year, previous_month)

        if previous_month_total > 0:
            growth_percentage = ((current_month_total - previous_month_total) / previous_month_total) * 100
        else:
            growth_percentage = 100 if current_month_total > 0 else 0

        stats[group_name] = {
            'title': display_name,
            'total': total,
            'last_updated': last_updated or today.strftime("%d/%m/%Y"),
            'growth_percentage': round(growth_percentage, 2),
            'is_positive_growth': growth_percentage >= 0
        }

    return stats
    

@login_required(login_url='login')
@role_required('data manager')
def data_manager_dashboard(request):
    context = {
        'stats': dashboard_analytics()
    }
    return render(request, 'dashboard/data_manager.html', context)

@login_required(login_url='login')
@role_required('auditor')
def auditor_dashboard(request):
    context = {
        'stats': dashboard_analytics()
    }
    return render(request, 'dashboard/auditor.html', context)

@login_required(login_url='login')
@role_required('city admin')
def city_admin_dashboard(request):
    context = {
        'stats': dashboard_analytics()
    }
    return render(request, 'dashboard/city_admin.html', context)

@login_required
def universal_dashboard(request):
    context = {
        "dashboard_title": "Dashboard",
        "stats": {
            "landfill": 0,
            "recovered": 0,
            "food": 0,
            "compost": 0,
        },
        "audit_locations": [
            {
                "name": "Downtown Center 1",
                "volume": "200",
                "type": "Compost",
                "collected_at": "Compost Facility",
                "date": "January 10, 2025",
                "compliant": False,
            },
            {
                "name": "Downtown Center 3",
                "volume": "200",
                "type": "Compost",
                "collected_at": "Compost Facility",
                "date": "January 10, 2025",
                "compliant": True,
            },
        ]
    }
    return render(request, "dashboard/universal.html", context)