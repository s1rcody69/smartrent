from rest_framework import serializers
from .models import Property, Unit


class UnitSerializer(serializers.ModelSerializer):
    # Read-only field that returns the human-readable status label e.g. "Vacant"
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Read-only field that returns the human-readable unit type label e.g. "Villa"
    unit_type_display = serializers.CharField(source='get_unit_type_display', read_only=True)

    class Meta:
        model = Unit
        fields = [
            'id',
            'property',
            'unit_number',
            'unit_type',
            'unit_type_display',
            'floor',
            'bedrooms',
            'bathrooms',
            'rent_amount',
            'status',
            'status_display',
            'description',
            'created_at',
            'updated_at',
        ]
        # These fields are set automatically and should never be changed via API
        read_only_fields = ['id', 'created_at', 'updated_at']


class PropertySerializer(serializers.ModelSerializer):
    # Nested serializer — returns all units when viewing a property detail
    # many=True because one property has many units
    # read_only=True because units are managed through their own endpoints
    units = UnitSerializer(many=True, read_only=True)

    # Returns the landlord's full name for display purposes
    landlord_name = serializers.CharField(
        source='landlord.user.full_name',
        read_only=True
    )

    # Read-only field that returns the human-readable property type label
    property_type_display = serializers.CharField(
        source='get_property_type_display',
        read_only=True
    )

    class Meta:
        model = Property
        fields = [
            'id',
            'landlord',
            'landlord_name',
            'property_type',
            'property_type_display',
            'name',
            'address',
            'city',
            'description',
            'cover_image',
            'total_units',
            'is_active',
            'units',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'landlord', 'total_units', 'created_at', 'updated_at']


class PropertyListSerializer(serializers.ModelSerializer):
    # Lightweight serializer for list views — no nested units
    # Used when returning many properties to avoid heavy queries
    landlord_name = serializers.CharField(
        source='landlord.user.full_name',
        read_only=True
    )

    # Read-only field that returns the human-readable property type label
    property_type_display = serializers.CharField(
        source='get_property_type_display',
        read_only=True
    )

    
    vacant_units = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id',
            'landlord',
            'landlord_name',
            'property_type',
            'property_type_display',
            'name',
            'address',
            'city',
            'cover_image',
            'total_units',
            'vacant_units',  
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'landlord', 'total_units', 'created_at']

    def get_vacant_units(self, obj):
        """Return the number of vacant units for this property."""
        return obj.units.filter(status='vacant').count()