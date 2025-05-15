from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def report_location_view(request):
    return render(request, "reports/report-location.html")

@login_required(login_url='login')
def reports_view(request):
    return render(request, "reports/reports.html")