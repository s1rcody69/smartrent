from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import MaintenanceRequest
from .serializers import MaintenanceRequestSerializer
from leases.models import Lease
from accounts.models import LandlordProfile
from accounts.models import TenantProfile
from properties.models import Unit


class IsLandlordOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if request.user.role == 'landlord':
            return obj.unit.property.landlord.user == request.user
        if request.user.role == 'tenant':
            return obj.tenant.user == request.user
        return False


class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [IsLandlordOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category']
    search_fields = ['title', 'description', 'tenant__user__email']
    ordering_fields = ['created_at', 'priority', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user

        if user.role == 'admin':
            return MaintenanceRequest.objects.all()

        if user.role == 'landlord':
            try:
                landlord_profile = user.landlord_profile
                return MaintenanceRequest.objects.filter(
                    unit__property__landlord=landlord_profile
                )
            except LandlordProfile.DoesNotExist:
                return MaintenanceRequest.objects.none()

        if user.role == 'tenant':
            try:
                return MaintenanceRequest.objects.filter(
                    tenant=user.tenant_profile
                )
            except Exception:
                return MaintenanceRequest.objects.none()

        return MaintenanceRequest.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.role == 'tenant':
            # Derive unit from tenant's active lease
            active_lease = Lease.objects.filter(
                tenant=user.tenant_profile,
                status='active'
            ).first()

            if not active_lease:
                from rest_framework.exceptions import ValidationError
                raise ValidationError(
                    'You do not have an active lease. Cannot submit a maintenance request.'
                )

            serializer.save(
                tenant=user.tenant_profile,
                unit=active_lease.unit
            )
        else:
            # Admin or landlord creating on behalf of tenant
            tenant_id = self.request.data.get('tenant')
            unit_id = self.request.data.get('unit')

            try:
                tenant = TenantProfile.objects.get(id=tenant_id)
                unit = Unit.objects.get(id=unit_id)
            except (TenantProfile.DoesNotExist, Unit.DoesNotExist):
                from rest_framework.exceptions import ValidationError
                raise ValidationError('Invalid tenant or unit.')

            serializer.save(tenant=tenant, unit=unit)