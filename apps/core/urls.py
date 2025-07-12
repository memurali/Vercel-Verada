from django.urls import path
from apps.core.views import (
    master_commodity_dashboard, 
    commodity_form_view, 
    add_commodity_ajax,
    upload_commodity_document,
    unit_form_view,
    add_unit_ajax,
    edit_commodity_view,
    update_commodity,
    commodity_bulk_import_view,
    upload_excel,
    add_commodities_form,
    commodities_type_dashboard,
    create_commodity_type,
    edit_commodity_type_page,
    edit_commodity_type,
    edit_units_view,
    update_units,
    units_names_dashboard
)
from apps.core.bulk_upload_view import bulk_upload_commodity_data

app_name = "core"

urlpatterns = [
    path("dashboard/", master_commodity_dashboard, name="dashboard"),
    path('edit/<int:id>/', edit_commodity_view, name='edit_commodity'),
    path('update/', update_commodity, name='update_commodity'),

    path("add/", commodity_form_view, name="commondity_form"),
    path("add/submit/", add_commodity_ajax, name="add_commodities"),
    path("upload-document/", upload_commodity_document, name="upload_doc_commoditi"),
    path("unit/form/", unit_form_view, name="unit_form"),
    path("unit/add/", add_unit_ajax, name="add_unit"),

    path('units/type/', units_names_dashboard, name='units_names_dashboard'),
    path('units/edit/<int:id>/', edit_units_view, name='edit_units_view'),
    path('units/update/<int:pk>/', update_units, name='update_units'),

    path("commodity/bulk-import/", commodity_bulk_import_view, name="commodity_bulk_import_view"),
    path('upload_excel/',upload_excel,name='upload_excel'),
    path('save_mapped_data/', bulk_upload_commodity_data, name='save_mapped_data'),

    path('add/type/', add_commodities_form, name="add_commodities_type"),
    path('type/dashboard/', commodities_type_dashboard, name="commodities_type_dashboard"),
    path('create/type/', create_commodity_type, name='create_commodity_type'),
    path('edit/type/<int:pk>/', edit_commodity_type, name='edit_commodity_type'),
    path('edit/type/page/<int:pk>/', edit_commodity_type_page, name='edit_commodity_type_page'),
]
