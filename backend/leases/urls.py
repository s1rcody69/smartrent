from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeaseViewSet

# Router automatically generates all CRUD endpoints for leases
router = DefaultRouter()
router.register(r'leases', LeaseViewSet, basename='lease')

urlpatterns = [
    path('', include(router.urls)),
]