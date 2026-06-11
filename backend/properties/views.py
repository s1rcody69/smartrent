from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from .models import Property, Unit
from .serializers import PropertySerializer, PropertyListSerializer, UnitSerializer
from accounts.models import LandlordProfile


class IsLandlordOrAdmin(permissions.BasePermission):
    # Custom permission — only landlords and admins can create/edit properties
    def has_permission(self, request, view):
        # Allow read access to all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        # Write access only for landlords and admins
        return request.user.is_authenticated and request.user.role in ['landlord', 'admin']

    def has_object_permission(self, request, view, obj):
        # Allow read access to all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        # Admins can edit any property
        if request.user.role == 'admin':
            return True
        # Landlords can only edit their own properties
        if request.user.role == 'landlord':
            return obj.landlord.user == request.user
        return False


class PropertyViewSet(viewsets.ModelViewSet):
    # ModelViewSet provides list, create, retrieve, update, destroy automatically
    permission_classes = [IsLandlordOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Fields that can be filtered via query params e.g. ?city=Nairobi&is_active=true
    filterset_fields = ['city', 'is_active']

    # Fields that can be searched via ?search=keyword
    search_fields = ['name', 'address', 'city', 'description']

    # Fields that can be ordered via ?ordering=created_at
    ordering_fields = ['created_at', 'name', 'city', 'total_units']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user

        # Admins can see all properties
        if user.role == 'admin':
            return Property.objects.all()

        # Landlords can only see their own properties
        if user.role == 'landlord':
            try:
                landlord_profile = user.landlord_profile
                return Property.objects.filter(landlord=landlord_profile)
            except LandlordProfile.DoesNotExist:
                return Property.objects.none()

        # Tenants can only see active properties
        return Property.objects.filter(is_active=True)

    def get_serializer_class(self):
        # Use lightweight serializer for list view
        # Use full serializer with nested units for detail view
        if self.action == 'list':
            return PropertyListSerializer
        return PropertySerializer

    def perform_create(self, serializer):
        # Automatically assign the landlord profile when creating a property
        landlord_profile = self.request.user.landlord_profile
        serializer.save(landlord=landlord_profile)

    def perform_update(self, serializer):
        instance = serializer.save()
        # Update total_units count whenever property is updated
        instance.total_units = instance.units.count()
        instance.save()


class UnitViewSet(viewsets.ModelViewSet):
    serializer_class = UnitSerializer
    permission_classes = [IsLandlordOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Fields that can be filtered via query params e.g. ?status=vacant&bedrooms=2
    filterset_fields = ['status', 'bedrooms', 'bathrooms']

    search_fields = ['unit_number', 'description']
    ordering_fields = ['rent_amount', 'unit_number', 'created_at']
    ordering = ['unit_number']

    def get_queryset(self):
        user = self.request.user

        # Admins can see all units
        if user.role == 'admin':
            return Unit.objects.all()

        # Landlords can only see units in their own properties
        if user.role == 'landlord':
            try:
                landlord_profile = user.landlord_profile
                return Unit.objects.filter(property__landlord=landlord_profile)
            except LandlordProfile.DoesNotExist:
                return Unit.objects.none()

        # Tenants can only see vacant units
        return Unit.objects.filter(status='vacant')

    def perform_create(self, serializer):
        unit = serializer.save()
        # Update the total_units count on the parent property
        property_instance = unit.property
        property_instance.total_units = property_instance.units.count()
        property_instance.save()

    def perform_destroy(self, instance):
        property_instance = instance.property
        instance.delete()
        # Recalculate total_units after a unit is deleted
        property_instance.total_units = property_instance.units.count()
        property_instance.save()
