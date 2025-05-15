"""
URL configuration for reuse_track project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import permissions
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.api_urls')),

    # Schema generation endpoint
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Redoc UI (optional)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('', lambda request: redirect('/dashboard')),

    path('', include('apps.users.api_urls')),
    path('', include('apps.common.urls')),
    path("agreements/", include("apps.agreements.urls")),
    path("generators/", include("apps.waste_generators.urls", namespace="generators")),
    path("collectors/", include("apps.waste_collectors.urls", namespace="collectors")),
    path("commodities/", include("apps.core.urls", namespace="core")),
    path("audits/", include("apps.audits.urls")),
    path("waste/", include("apps.waste_source_group.urls", namespace="waste_source_group")),
    path('client/commodities/', include("apps.commodities.urls", namespace="commodities"))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)