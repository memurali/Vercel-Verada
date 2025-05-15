from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.audits.models import Audit, AuditCommoditi

@login_required(login_url='login')
def audit_dashboard_view(request):
    # Example data (replace with real DB query)
    if request.user.is_cityadmin:
        upcoming_audits = Audit.objects.select_related('officer', 'destination').filter(status__in=['P','S'])

        verification_audits = Audit.objects.select_related('officer', 'destination')\
            .prefetch_related('audit_commoditi')\
            .filter(status__in=['F','C'], audit_type='verification')

        initial_audits = Audit.objects.select_related('officer', 'destination')\
            .prefetch_related('audit_commoditi')\
            .filter(status__in=['F','C'], audit_type='initial')
    else:
        upcoming_audits = Audit.objects.select_related('officer', 'destination').filter(status__in=['P','S'], officer__user=request.user)

        verification_audits = Audit.objects.select_related('officer', 'destination')\
            .prefetch_related('audit_commoditi')\
            .filter(status__in=['F','C'], audit_type='verification', officer__user=request.user)

        initial_audits = Audit.objects.select_related('officer', 'destination')\
            .prefetch_related('audit_commoditi')\
            .filter(status__in=['F','C'], audit_type='initial', officer__user=request.user)
        
    return render(request, "audits/audit.html", {
        "upcoming_audits": upcoming_audits,
        "verification_audits": verification_audits,
        "inital_audits": initial_audits
    })