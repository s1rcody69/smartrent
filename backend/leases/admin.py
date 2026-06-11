from django.contrib import admin
from .models import Lease


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):

    list_display = [
        'tenant',
        'unit',
        'rent_amount',
        'start_date',
        'end_date',
        'status',
        'created_at'
    ]

    # Filter leases by status in the sidebar
    list_filter = ['status']

    search_fields = [
        'tenant__user__email',
        'tenant__user__first_name',
        'unit__unit_number',
        'unit__property__name'
    ]

    readonly_fields = ['created_at', 'updated_at']
