from django.urls import path
from . import views
from apps.waste_generators.pickup_views import (
    waste_pickup_dashboard, 
    waste_pickup_form_view, 
    submit_waste_pickup,
    get_pickup_food_type,
    waste_Pickups_import,
    waste_Pickups_download_template,
    download_template,
    upload_excel,
    save_mapped_data,
    download_temp_getting_names,
    edit_pickup_view,
    update_pickup
)

app_name = "generators"

urlpatterns = [
    path("dashboard/", views.generator_dashboard_view, name="waste_generator_dashboard"),
    path("edit/<int:pk>/", views.generator_form_edit_view, name="edit_generator"),

    path("add/", views.generator_form_view, name="add_generator"),
    path("save/", views.save_generator, name="save_generator"),

    #PICKUPS
    path("pickup/dashboard/", waste_pickup_dashboard, name="waste_pickup_dashboard"),
    path("pickup/form/", waste_pickup_form_view, name="waste_pickup_form"),
    path("pickup/submit/", submit_waste_pickup, name="submit_waste_pickup"),
    path("get/food_type/<int:group_id>/", get_pickup_food_type, name="get_pickup_food_type"),
    path('edit_pickup_view/<int:pickup_id>/', edit_pickup_view, name='edit_pickup_view'),
    path('update/', update_pickup, name='update_pickup'),



    # Import 
    path('waste_Pickups_import/', waste_Pickups_import, name='waste_Pickups_import'),
    path('waste_Pickups_download_template/', waste_Pickups_download_template, name='waste_Pickups_download_template'),

    # Import and download template 
    path('download-template/', download_template, name='download_template'),
    path('upload_excel', upload_excel, name='upload_excel'),
    path('save_mapped_data', save_mapped_data, name='save_mapped_data'),
    path('download_temp_getting_names', download_temp_getting_names, name='download_temp_getting_names'),
    

]
