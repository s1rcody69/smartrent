from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeaseViewSet, LeaseTerminationRequestViewSet

# Router automatically generates all CRUD endpoints for leases
router = DefaultRouter()
router.register(r'leases', LeaseViewSet, basename='lease')

# Router generates CRUD + the custom approve/reject action endpoints:
# POST /api/lease-terminations/{id}/approve/
# POST /api/lease-terminations/{id}/reject/
router.register(r'lease-terminations', LeaseTerminationRequestViewSet, basename='lease-termination')

urlpatterns = [
    path('', include(router.urls)),
]