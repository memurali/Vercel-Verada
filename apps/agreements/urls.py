from django.urls import path
from apps.agreements.views import (
    agreement_dashboard_view, 
    agreement_form_view, 
    agreement_ajax_submit,
    agreement_edit_form,
    agreement_ajax_update
)

app_name = 'agreements'

urlpatterns = [
    path("dashboard/", agreement_dashboard_view, name="dashboard"),
    path("form/", agreement_form_view, name="form"),
    path("ajax-submit/", agreement_ajax_submit, name="ajax_submit"),

    path("edit/<int:id>/", agreement_edit_form, name="edit_form"),
    path("ajax-submit/", agreement_ajax_submit, name="ajax_submit"),
    path("update/", agreement_ajax_update, name="agreement_ajax_update"),
]
