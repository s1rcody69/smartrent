from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import MaintenanceRequest
from .serializers import MaintenanceRequestSerializer
from leases.models import Lease


class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceRequestSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Fields that can be filtered via query params
    filterset_fields = ['status', 'priority', 'category']
    search_fields = ['title', 'description', 'tenant__user__email']
    ordering_fields = ['created_at', 'priority', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        # Temporarily return all requests for teacher review
        return MaintenanceRequest.objects.all()

    def perform_create(self, serializer):
        request = self.request

        if request.user.is_authenticated and request.user.role == 'tenant':
            # Get the active lease from context set during validation
            active_lease = self.get_serializer().context.get('active_lease')

            if not active_lease:
                # Fallback — find active lease directly
                active_lease = Lease.objects.filter(
                    tenant=request.user.tenant_profile,
                    status='active'
                ).first()

            serializer.save(
                tenant=request.user.tenant_profile,
                unit=active_lease.unit
            )
        else:
            # For teacher review — allow creation without auth
            # Unit and tenant must be provided manually
            serializer.save()