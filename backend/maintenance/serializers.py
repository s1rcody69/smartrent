from rest_framework import serializers
from .models import MaintenanceRequest
from leases.models import Lease


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    # Human-readable display values for choice fields
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    # Tenant and unit details for display
    tenant_name = serializers.CharField(source='tenant.user.full_name', read_only=True)
    tenant_email = serializers.CharField(source='tenant.user.email', read_only=True)
    unit_number = serializers.CharField(source='unit.unit_number', read_only=True)
    property_name = serializers.CharField(source='unit.property.name', read_only=True)

    class Meta:
        model = MaintenanceRequest
        fields = [
            'id',
            'tenant',
            'tenant_name',
            'tenant_email',
            'unit',
            'unit_number',
            'property_name',
            'title',
            'description',
            'category',
            'category_display',
            'priority',
            'priority_display',
            'status',
            'status_display',
            'image',
            'landlord_notes',
            'created_at',
            'updated_at',
        ]
        # Unit and tenant are set automatically — never from request body
        read_only_fields = ['id', 'tenant', 'unit', 'created_at', 'updated_at']

    def validate(self, data):
        request = self.context.get('request')

        # Only validate active lease on creation
        if not self.instance and request and request.user.is_authenticated:
            if request.user.role == 'tenant':
                try:
                    tenant_profile = request.user.tenant_profile
                except Exception:
                    raise serializers.ValidationError(
                        'Tenant profile not found.'
                    )

                # Check if tenant has an active lease
                active_lease = Lease.objects.filter(
                    tenant=tenant_profile,
                    status='active'
                ).first()

                if not active_lease:
                    raise serializers.ValidationError(
                        'You do not have an active lease. Cannot submit a maintenance request.'
                    )

                # Store the unit for use in the view
                self.context['active_lease'] = active_lease

        return data