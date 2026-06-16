from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

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
    permission_classes = [IsLandlordOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'is_active', 'property_type']
    search_fields = ['name', 'address', 'city', 'description']
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
        if self.action == 'list':
            return PropertyListSerializer
        return PropertySerializer

    def perform_create(self, serializer):
        # Automatically assign the landlord profile when creating a property
        landlord_profile = self.request.user.landlord_profile
        serializer.save(landlord=landlord_profile)

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.total_units = instance.units.count()
        instance.save()


class UnitViewSet(viewsets.ModelViewSet):
    serializer_class = UnitSerializer
    permission_classes = [IsLandlordOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'bedrooms', 'bathrooms', 'unit_type']
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
        property_instance = unit.property
        property_instance.total_units = property_instance.units.count()
        property_instance.save()

    def perform_destroy(self, instance):
        property_instance = instance.property
        instance.delete()
        property_instance.total_units = property_instance.units.count()
        property_instance.save()
