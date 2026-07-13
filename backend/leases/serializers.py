from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Lease, LeaseTerminationRequest
from accounts.models import TenantProfile
from properties.models import Unit
from payments.models import RentInvoice

User = get_user_model()


class LeaseSerializer(serializers.ModelSerializer):
    # Human-readable status label
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    # Tenant details for display
    tenant_name = serializers.CharField(
        source='tenant.user.full_name',
        read_only=True
    )
    tenant_email = serializers.CharField(
        source='tenant.user.email',
        read_only=True
    )

    # Unit details for display
    unit_number = serializers.CharField(
        source='unit.unit_number',
        read_only=True
    )
    property_name = serializers.CharField(
        source='unit.property.name',
        read_only=True
    )

    # 👇 ADDED: Landlord name for display
    landlord_name = serializers.CharField(
        source='unit.property.landlord.user.full_name',
        read_only=True
    )

    class Meta:
        model = Lease
        fields = [
            'id',
            'tenant',
            'tenant_name',
            'tenant_email',
            'unit',
            'unit_number',
            'property_name',
            'landlord_name',  
            'rent_amount',
            'deposit_amount',
            'start_date',
            'end_date',
            'status',
            'status_display',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'tenant': {'required': False},
        }

    def validate(self, data):
        unit = data.get('unit')

        # On creation only — check if unit is already occupied
        if not self.instance:
            if unit and unit.status == 'occupied':
                raise serializers.ValidationError({
                    'unit': 'This unit is already occupied.'
                })

        # Validate that end_date is after start_date
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date:
            if end_date <= start_date:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date.'
                })

        return data

    def create(self, validated_data):
        # Automatically set rent_amount from the unit if not provided
        if 'rent_amount' not in validated_data:
            validated_data['rent_amount'] = validated_data['unit'].rent_amount
        return super().create(validated_data)


class LeaseTerminationRequestSerializer(serializers.ModelSerializer):
    # Human-readable status for display
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    # Lease details for context
    tenant_name = serializers.CharField(
        source='lease.tenant.user.full_name',
        read_only=True
    )
    unit_number = serializers.CharField(
        source='lease.unit.unit_number',
        read_only=True
    )
    property_name = serializers.CharField(
        source='lease.unit.property.name',
        read_only=True
    )
    deposit_amount = serializers.DecimalField(
        source='lease.deposit_amount',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    # Who requested and who reviewed — display names only
    requested_by_name = serializers.CharField(
        source='requested_by.full_name',
        read_only=True
    )
    reviewed_by_name = serializers.CharField(
        source='reviewed_by.full_name',
        read_only=True,
        allow_null=True
    )

    # Unpaid invoices count — warning for landlord before approving
    unpaid_invoices_count = serializers.SerializerMethodField()

    class Meta:
        model = LeaseTerminationRequest
        fields = [
            'id',
            'lease',
            'tenant_name',
            'unit_number',
            'property_name',
            'deposit_amount',
            'requested_by',
            'requested_by_name',
            'reason',
            'requested_vacate_date',
            'status',
            'status_display',
            'deposit_forfeited',
            'deposit_note',
            'reviewed_by',
            'reviewed_by_name',
            'reviewed_at',
            'review_note',
            'unpaid_invoices_count',
            'created_at',
            'updated_at',
        ]
        # These are set by the system, never by API input
        read_only_fields = [
            'id',
            'requested_by',
            'deposit_forfeited',
            'deposit_note',
            'reviewed_by',
            'reviewed_at',
            'status',
            'created_at',
            'updated_at',
        ]

    def get_unpaid_invoices_count(self, obj):
        # Count unpaid invoices on this lease — used as a warning on the frontend
        return RentInvoice.objects.filter(
            lease=obj.lease,
            status__in=['pending', 'overdue']
        ).count()

    def validate(self, data):
        request = self.context.get('request')

        # On creation only
        if not self.instance:
            lease = data.get('lease')

            if not lease:
                raise serializers.ValidationError({'lease': 'Lease is required.'})

            # Only allow requests against active leases
            if lease.status != 'active':
                raise serializers.ValidationError({
                    'lease': 'You can only request early termination on an active lease.'
                })

            # Check if there is already a pending request on this lease
            existing = LeaseTerminationRequest.objects.filter(
                lease=lease,
                status='pending'
            ).exists()
            if existing:
                raise serializers.ValidationError({
                    'lease': 'There is already a pending termination request on this lease.'
                })

            # Validate requested vacate date is in the future
            from datetime import date
            if data.get('requested_vacate_date') and data['requested_vacate_date'] <= date.today():
                raise serializers.ValidationError({
                    'requested_vacate_date': 'Vacate date must be in the future.'
                })

        return data
