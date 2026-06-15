from django.contrib import admin
from .models import MaintenanceRequest


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):

    list_display = [
        'title',
        'tenant',
        'unit',
        'category',
        'priority',
        'status',
        'created_at'
    ]

    # Filter by status and priority in the sidebar
    list_filter = ['status', 'priority', 'category']

    search_fields = [
        'title',
        'description',
        'tenant__user__email',
        'unit__unit_number'
    ]

    readonly_fields = ['created_at', 'updated_at']
