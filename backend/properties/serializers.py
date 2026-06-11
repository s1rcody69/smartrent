from rest_framework import serializers
from .models import Property, Unit


class UnitSerializer(serializers.ModelSerializer):
    # Read-only field that returns the human-readable status label
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Unit
        fields = [
            'id',
            'property',
            'unit_number',
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
    # Nested serializer — returns all units when viewing a property
    # many=True because one property has many units
    # read_only=True because units are managed through their own endpoints
    units = UnitSerializer(many=True, read_only=True)

    # Returns the landlord's full name for display purposes
    landlord_name = serializers.CharField(
        source='landlord.user.full_name',
        read_only=True
    )

    class Meta:
        model = Property
        fields = [
            'id',
            'landlord',
            'landlord_name',
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
        read_only_fields = ['id', 'total_units', 'created_at', 'updated_at']


class PropertyListSerializer(serializers.ModelSerializer):
    # Lightweight serializer for list views — no nested units
    # Used when returning many properties to avoid heavy queries
    landlord_name = serializers.CharField(
        source='landlord.user.full_name',
        read_only=True
    )

    class Meta:
        model = Property
        fields = [
            'id',
            'landlord',
            'landlord_name',
            'name',
            'address',
            'city',
            'cover_image',
            'total_units',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'total_units', 'created_at']