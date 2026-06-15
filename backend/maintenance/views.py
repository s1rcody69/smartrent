from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import MaintenanceRequest
from .serializers import MaintenanceRequestSerializer
from accounts.models import TenantProfile
from properties.models import Unit


class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceRequestSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category']
    search_fields = ['title', 'description', 'tenant__user__email']
    ordering_fields = ['created_at', 'priority', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        # Temporarily return all requests for teacher review
        return MaintenanceRequest.objects.all()

    def perform_create(self, serializer):
        # Get tenant and unit directly from request data for teacher review
        # When auth is re-enabled this will use request.user.tenant_profile instead
        tenant_id = self.request.data.get('tenant')
        unit_id = self.request.data.get('unit')

        try:
            tenant = TenantProfile.objects.get(id=tenant_id)
            unit = Unit.objects.get(id=unit_id)
        except (TenantProfile.DoesNotExist, Unit.DoesNotExist):
            from rest_framework.exceptions import ValidationError
            raise ValidationError('Invalid tenant or unit.')

        serializer.save(tenant=tenant, unit=unit)