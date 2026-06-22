from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, LandlordProfile, TenantProfile    


# @admin.register decorator registers the User model with the admin site
# This replaces the older admin.site.register(User) syntax
@admin.register(User)
class UserAdmin(BaseUserAdmin):

    # Columns visible in the user list view inside admin panel
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'is_verified', 'date_joined']

    # Sidebar filters on the right side of the list view
    list_filter = ['role', 'is_active', 'is_verified']

    # Fields that the search bar will query against
    search_fields = ['email', 'first_name', 'last_name']

    # Default ordering — most recently joined users appear first
    ordering = ['-date_joined']

    # fieldsets controls the layout of the user detail/edit page
    # Each tuple is (section_title, {options})
    fieldsets = (
        ('Login Credentials', {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Role & Status', {'fields': ('role', 'is_active', 'is_verified', 'is_staff', 'is_superuser')}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('date_joined', 'updated_at')}),
    )

    # These fields are displayed but cannot be edited through the admin panel
    readonly_fields = ['date_joined', 'updated_at']

    # add_fieldsets controls the layout of the create new user form in admin
    # 'wide' is a CSS class that makes the form wider for better readability
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )

# Register the landlord and tenant profiles with the admin site

@admin.register(LandlordProfile)
class LandlordProfileAdmin(admin.ModelAdmin):

    # Columns visible in the landlord profile list view
    list_display = ['user', 'created_at']

    # Fields the search bar will query against
    search_fields = ['user__email', 'user__first_name', 'user__last_name']

    # These fields cannot be edited through the admin panel
    readonly_fields = ['created_at', 'updated_at']

@admin.register(TenantProfile)
class TenantProfileAdmin(admin.ModelAdmin):

    # Columns visible in the tenant profile list view
    list_display = ['user', 'national_id', 'occupation', 'created_at']

    # Sidebar filters
    list_filter = ['occupation']

    # Fields the search bar will query against
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'national_id']

    # These fields cannot be edited through the admin panel
    readonly_fields = ['created_at', 'updated_at']