from django.urls import path
from . import views

app_name = "waste_source_group"

urlpatterns = [
    path("group/dashboard/", views.waste_group_master_dashboard, name="waste_group_master_dashboard"),
    path("group/form/", views.waste_group_master_form, name="waste_group_master_form"),
    path("source/dashboard/", views.waste_source_master_dashboard, name="waste_source_master_dashboard"),
    path("source/form/", views.waste_source_master_form, name="waste_source_master_form"),

    path('submit/group/form/', views.submit_waste_group_master, name='waste_group_master_submit'),
    path("source/store/", views.store_waste_source, name="store_waste_source"),

    path("ajax/get-group-description/", views.get_group_description, name="get_group_description"),

    path('edit/<int:id>/', views.edit_group_view, name='edit_group_view'),
    path('update/', views.update_waste_group, name='update_waste_group'),
    path('delete/', views.delete_waste_group_master, name='delete_waste_group_master'),

    path('source/edit/<int:id>/', views.edit_group_master_view, name='edit_group_master_view'),
    path('source/updates/', views.update_waste_group_master, name='update_waste_group_master'),
    path('source/delete/', views.delete_waste_source_master, name='update_waste_group')

]
