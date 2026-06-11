from django.contrib import admin
from .models import Property, Unit


class UnitInline(admin.TabularInline):
    # Inline allows us to manage units directly from the property detail page
    model = Unit
    extra = 0
    readonly_fields = ['created_at', 'updated_at']
    fields = ['unit_number', 'floor', 'bedrooms', 'bathrooms', 'rent_amount', 'status']


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):

    # Show units inline when viewing a property
    inlines = [UnitInline]

    list_display = ['name', 'city', 'landlord', 'total_units', 'is_active', 'created_at']
    list_filter = ['is_active', 'city']
    search_fields = ['name', 'address', 'city', 'landlord__user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):

    list_display = ['unit_number', 'property', 'bedrooms', 'bathrooms', 'rent_amount', 'status']
    list_filter = ['status', 'bedrooms']
    search_fields = ['unit_number', 'property__name']
    readonly_fields = ['created_at', 'updated_at']
