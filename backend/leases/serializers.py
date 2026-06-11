from rest_framework import serializers
from django.utils import timezone
from .models import Lease
from accounts.models import TenantProfile
from properties.models import Unit


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

    def validate(self, data):
        unit = data.get('unit')
        status = data.get('status', 'active')

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