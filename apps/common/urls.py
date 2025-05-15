# apps/dashboard/urls.py

from django.urls import path
from apps.common.views import dashboard_view
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = "dashboard"

urlpatterns = [
    path("dashboard", dashboard_view, name="dashboard"),  # Accessible via /dashboard/
    path('dashboard/data-manager/', views.data_manager_dashboard, name="data_manager"),
    path('dashboard/auditor/', views.auditor_dashboard, name="auditor"),
    path('dashboard/city-admin/', views.city_admin_dashboard, name="city_admin"),
    path("dashboard/universal/", views.universal_dashboard, name="dashboard_universal"),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)