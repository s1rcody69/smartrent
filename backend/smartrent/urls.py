"""
URL configuration for smartrent project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin panel
    path('admin/', admin.site.urls),
    
    # Authentication endpoints
    path('api/auth/', include('accounts.urls')),
    
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
    
    # Accounts endpoints
    path('api/', include('accounts.urls'))
]