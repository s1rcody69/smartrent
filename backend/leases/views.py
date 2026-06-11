from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Lease
from .serializers import LeaseSerializer
from accounts.models import LandlordProfile


class IsLandlordOrAdmin(permissions.BasePermission):
    # Landlords and admins can create and manage leases
    # Tenants can only view their own leases
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admins can access any lease
        if request.user.role == 'admin':
            return True
        # Landlords can access leases for their own properties
        if request.user.role == 'landlord':
            return obj.unit.property.landlord.user == request.user
        # Tenants can only view their own leases
        if request.user.role == 'tenant':
            return obj.tenant.user == request.user
        return False


class LeaseViewSet(viewsets.ModelViewSet):
    serializer_class = LeaseSerializer
    permission_classes = [IsLandlordOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Fields that can be filtered via query params
    filterset_fields = ['status', 'unit__property']
    search_fields = ['tenant__user__email', 'tenant__user__first_name', 'unit__unit_number']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user

        # Admins can see all leases
        if user.role == 'admin':
            return Lease.objects.all()

        # Landlords can only see leases for their own properties
        if user.role == 'landlord':
            try:
                landlord_profile = user.landlord_profile
                return Lease.objects.filter(
                    unit__property__landlord=landlord_profile
                )
            except LandlordProfile.DoesNotExist:
                return Lease.objects.none()

        # Tenants can only see their own leases
        if user.role == 'tenant':
            try:
                return Lease.objects.filter(tenant=user.tenant_profile)
            except Exception:
                return Lease.objects.none()

        return Lease.objects.none()
