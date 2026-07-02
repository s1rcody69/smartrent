from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django.db.models import ProtectedError
from django_filters.rest_framework import DjangoFilterBackend

from .models import Property, Unit
from .serializers import PropertySerializer, PropertyListSerializer, UnitSerializer
from accounts.models import LandlordProfile


class IsLandlordOrAdmin(permissions.BasePermission):
    # Custom permission — only landlords and admins can create/edit properties
    def has_permission(self, request, view):
        # Allow read access to anyone — authenticated or not
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write access only for landlords and admins
        return request.user.is_authenticated and request.user.role in ['landlord', 'admin']

    def has_object_permission(self, request, view, obj):
        # Allow read access to anyone — authenticated or not
        if request.method in permissions.SAFE_METHODS:
            return True
        # Admins can edit any property or unit
        if request.user.role == 'admin':
            return True
        # Landlords can only edit things tied to their own properties
        if request.user.role == 'landlord':
            # obj is a Property — it has .landlord directly
            if hasattr(obj, 'landlord'):
                return obj.landlord.user == request.user
            # obj is a Unit — reach the landlord through its parent property
            if hasattr(obj, 'property'):
                return obj.property.landlord.user == request.user
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

        # Unauthenticated users — public landing page, show active properties only
        if not user.is_authenticated:
            return Property.objects.filter(is_active=True)

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

        # Tenants and any other authenticated users see active properties
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

        # Unauthenticated users — show all units so property detail pages work
        if not user.is_authenticated:
            return Unit.objects.filter(property__is_active=True)

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

        # Tenants and authenticated users see units in active properties
        return Unit.objects.filter(property__is_active=True)

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

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {'error': 'Cannot delete this unit because it has an active lease attached. Terminate the lease first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
