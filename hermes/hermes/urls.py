"""
URL configuration for hermes project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from tests import views
from tests.api import api
import sys
import os

# Add the health check view
sys.path.append(os.path.join(settings.BASE_DIR))
from health_check import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tests/", include("tests.urls")),
    # path("", views.index, name="index"),  # Removed, view no longer exists
    path("unicorn/", include("django_unicorn.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("api/", api.urls),  # Add the API urls
    path("health/", health_check, name="health_check"),  # Health check endpoint
    path("", include("django_prometheus.urls")),  # Add Prometheus metrics endpoint
]

# Serve static files in development and production
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # In production, static files should be served by the web server
    # But for Docker setup, we'll serve them through Django
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
