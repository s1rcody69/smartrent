from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    MeView,
    LandlordProfileView,
    TenantProfileView,
    AvailableTenantsListView,
    AdminUsersListView,  # 👈 New import
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
    path('landlord/profile/', LandlordProfileView.as_view(), name='landlord-profile'),
    path('tenant/profile/', TenantProfileView.as_view(), name='tenant-profile'),
    path('available-tenants/', AvailableTenantsListView.as_view(), name='available-tenants'),
    path('users/', AdminUsersListView.as_view(), name='admin-users'),  # 👈 New URL
]