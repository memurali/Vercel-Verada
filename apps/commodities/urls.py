from django.urls import path
from apps.commodities.views import client_commoditi_dashboard, add_client_commoditi, submit_client_commodities, edit_client_commodity_view
app_name = "commodities"

urlpatterns = [
    path('dashboard/', client_commoditi_dashboard, name='client_commoditi_dashboard'),
    path('add/', add_client_commoditi, name='add_client_commoditi'),
    path('mapping/submit/', submit_client_commodities, name='submit_client_commodities'),
    path('edit/<int:id>/', edit_client_commodity_view, name='edit_client_commodity_view'),

]

