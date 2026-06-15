"""
URL configuration for smartrent project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

urlpatterns = [
    # Django admi panel
    path('admin/', admin.site.urls),
    # Authentication endpoints
    path('api/auth/', include ('accounts.urls')),
     # Properties and units endpoints
    path('api/', include('properties.urls')),
    # Leases endpoints
    path('api/', include('leases.urls')),
    # Maintenance requests endpoints
    path('api/', include('maintenance.urls')),
    # Payments endpoints
     path('api/', include('payments.urls')),
    # Reports and dashboard endpoints
    path('api/', include('reports.urls')),
]
