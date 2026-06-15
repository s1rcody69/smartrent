from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Property, Unit
from .serializers import PropertySerializer, PropertyListSerializer, UnitSerializer
from accounts.models import LandlordProfile


class IsLandlordOrAdmin(permissions.BasePermission):
    # Custom permission — only landlords and admins can create/edit properties
    # Temporarily disabled — will be re-enabled after teacher review
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role in ['landlord', 'admin']

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        if request.user.role == 'admin':
            return True
        if request.user.role == 'landlord':
            return obj.landlord.user == request.user
        return False


class PropertyViewSet(viewsets.ModelViewSet):
    permission_classes = []
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'is_active']
    search_fields = ['name', 'address', 'city', 'description']
    ordering_fields = ['created_at', 'name', 'city', 'total_units']
    ordering = ['-created_at']

    def get_queryset(self):
        # Temporarily return all properties for teacher review
        return Property.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return PropertyListSerializer
        return PropertySerializer

    def perform_create(self, serializer):
        # Temporarily use first available landlord profile for teacher review
        landlord_profile = LandlordProfile.objects.first()
        serializer.save(landlord=landlord_profile)

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.total_units = instance.units.count()
        instance.save()


class UnitViewSet(viewsets.ModelViewSet):
    serializer_class = UnitSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'bedrooms', 'bathrooms']
    search_fields = ['unit_number', 'description']
    ordering_fields = ['rent_amount', 'unit_number', 'created_at']
    ordering = ['unit_number']

    def get_queryset(self):
        # Temporarily return all units for teacher review
        return Unit.objects.all()

    def perform_create(self, serializer):
        unit = serializer.save()
        property_instance = unit.property
        property_instance.total_units = property_instance.units.count()
        property_instance.save()

    def perform_destroy(self, instance):
        property_instance = instance.property
        instance.delete()
        property_instance.total_units = property_instance.units.count()
        property_instance.save()
