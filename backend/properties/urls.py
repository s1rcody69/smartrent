from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet, UnitViewSet

# Router automatically generates URLs for all viewset actions
router = DefaultRouter()

# Registers /api/properties/ and /api/properties/<id>/
router.register(r'properties', PropertyViewSet, basename='property')

# Registers /api/units/ and /api/units/<id>/
router.register(r'units', UnitViewSet, basename='unit')

urlpatterns = [
    path('', include(router.urls)),
]