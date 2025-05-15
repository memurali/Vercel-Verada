from django.urls import path
from apps.audits.views.audit_views import audit_dashboard_view
from apps.audits.views.audit_schedule import schedule_audit_form_view, schedule_audit_submit, get_addresses_by_locations
from apps.audits.views.audit_add import audit_form_view, audit_form_submit
from apps.audits.views.audit_report import audit_report_view

app_name = "audits"

urlpatterns = [
    path("dashboard/", audit_dashboard_view, name="dashboard"),

    # Lambda views for temporary usage
    path("audits/report/<int:audit_id>/", audit_report_view, name="audit_report"),
    path('audits/add/<int:audit_id>/', audit_form_view, name='add_audit'),

    path('audit/schedule/', schedule_audit_form_view, name='audit_schedule_form'),
    path('audit/schedule/submit/', schedule_audit_submit, name='audit_schedule_submit'),
    path('get-addresses/', get_addresses_by_locations, name='get_addresses_by_locations'),

    # path("add/audit/", audit_form_view, name="add_audit"),
    path("submit/audit/", audit_form_submit, name="submit_audit"),
]
