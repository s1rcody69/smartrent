from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import ProtectedError
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import Lease, LeaseTerminationRequest
from .serializers import LeaseSerializer, LeaseTerminationRequestSerializer
from accounts.models import LandlordProfile
from payments.models import RentInvoice


class IsLandlordOrAdmin(permissions.BasePermission):
    # Landlords and admins can create and manage leases
    # Tenants can only view their own leases
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if request.user.role == 'landlord':
            # Handle both Lease and LeaseTerminationRequest objects
            if hasattr(obj, 'unit'):
                return obj.unit.property.landlord.user == request.user
            if hasattr(obj, 'lease'):
                return obj.lease.unit.property.landlord.user == request.user
        if request.user.role == 'tenant':
            if hasattr(obj, 'tenant'):
                return obj.tenant.user == request.user
            if hasattr(obj, 'requested_by'):
                return obj.requested_by == request.user
        return False


class LeaseViewSet(viewsets.ModelViewSet):
    serializer_class = LeaseSerializer
    permission_classes = [IsLandlordOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'unit__property']
    search_fields = ['tenant__user__email', 'tenant__user__first_name', 'unit__unit_number']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user

        if user.role == 'admin':
            return Lease.objects.all()

        if user.role == 'landlord':
            try:
                landlord_profile = user.landlord_profile
                return Lease.objects.filter(
                    unit__property__landlord=landlord_profile
                )
            except LandlordProfile.DoesNotExist:
                return Lease.objects.none()

        if user.role == 'tenant':
            try:
                return Lease.objects.filter(tenant=user.tenant_profile)
            except Exception:
                return Lease.objects.none()

        return Lease.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        
        # If user is a tenant, auto-set the tenant field
        if user.role == 'tenant':
            try:
                tenant_profile = user.tenant_profile
                serializer.save(tenant=tenant_profile)
            except Exception:
                from rest_framework.exceptions import ValidationError
                raise ValidationError('Tenant profile not found.')
        else:
            # Landlord/admin creating lease - they must provide tenant
            serializer.save()

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {'error': 'Cannot delete this lease because it has invoices attached. Mark it terminated instead.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class LeaseTerminationRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaseTerminationRequestSerializer
    permission_classes = [IsLandlordOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'lease']
    ordering_fields = ['created_at', 'requested_vacate_date']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user

        if user.role == 'admin':
            # Admins see all termination requests
            return LeaseTerminationRequest.objects.all()

        if user.role == 'landlord':
            # Landlords see requests on leases for their own properties
            try:
                landlord_profile = user.landlord_profile
                return LeaseTerminationRequest.objects.filter(
                    lease__unit__property__landlord=landlord_profile
                )
            except LandlordProfile.DoesNotExist:
                return LeaseTerminationRequest.objects.none()

        if user.role == 'tenant':
            # Tenants only see their own requests
            return LeaseTerminationRequest.objects.filter(
                requested_by=user
            )

        return LeaseTerminationRequest.objects.none()

    def perform_create(self, serializer):
        # Automatically set requested_by to the current user
        # and deposit_forfeited to True — always non-refundable on early exit
        serializer.save(
            requested_by=self.request.user,
            deposit_forfeited=True,
        )

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        """
        Landlord or admin approves the termination request.
        Enforces: no unpaid invoices exist on the lease before approving.
        On approval: sets lease status to terminated, which triggers
        the Lease.save() override to flip the unit back to vacant.
        """
        termination_request = self.get_object()

        # Only pending requests can be approved
        if termination_request.status != 'pending':
            return Response(
                {'error': f'This request is already {termination_request.status}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for unpaid invoices — hard block if any exist
        unpaid_invoices = RentInvoice.objects.filter(
            lease=termination_request.lease,
            status__in=['pending', 'overdue']
        )
        if unpaid_invoices.exists():
            count = unpaid_invoices.count()
            return Response(
                {
                    'error': f'Cannot approve. This lease has {count} unpaid invoice(s). '
                             f'All outstanding rent must be settled before early termination can be approved.',
                    'unpaid_invoices_count': count,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # All clear — approve the request
        termination_request.status = 'approved'
        termination_request.reviewed_by = request.user
        termination_request.reviewed_at = timezone.now()
        termination_request.review_note = request.data.get('review_note', '')
        termination_request.save()

        # Terminate the lease — this triggers Lease.save() which flips
        # the unit status back to vacant automatically
        lease = termination_request.lease
        lease.status = 'terminated'
        lease.save()

        return Response({
            'message': 'Termination request approved. Lease has been terminated and unit is now vacant.',
            'lease_status': lease.status,
            'unit_status': lease.unit.status,
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        """
        Landlord or admin rejects the termination request.
        Lease remains active, unit remains occupied.
        """
        termination_request = self.get_object()

        # Only pending requests can be rejected
        if termination_request.status != 'pending':
            return Response(
                {'error': f'This request is already {termination_request.status}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        termination_request.status = 'rejected'
        termination_request.reviewed_by = request.user
        termination_request.reviewed_at = timezone.now()
        termination_request.review_note = request.data.get('review_note', '')
        termination_request.save()

        return Response({
            'message': 'Termination request rejected. Lease remains active.',
        }, status=status.HTTP_200_OK)