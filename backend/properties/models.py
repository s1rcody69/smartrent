import uuid
from django.db import models
from accounts.models import LandlordProfile


class Property(models.Model):

    # Property belongs to a landlord profile, not directly to a user
    # on_delete=CASCADE means if the landlord is deleted, their properties are deleted too
    landlord = models.ForeignKey(
        LandlordProfile,
        on_delete=models.CASCADE,
        related_name='properties'
    )

    # UUID primary key for security — same reasoning as the User model
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    # Cloudinary will store the URL of the uploaded cover image
    cover_image = models.ImageField(
        upload_to='property_images/',
        blank=True,
        null=True
    )

    # Automatically calculated from the number of units
    # We store it here for quick access without counting units every time
    total_units = models.PositiveIntegerField(default=0)

    # Soft delete — deactivating a property hides it without losing data
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'properties'
        ordering = ['-created_at']
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'

    def __str__(self):
        return f'{self.name} — {self.city}'


class Unit(models.Model):

    STATUS_CHOICES = (
        ('vacant', 'Vacant'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
    )

    # Unit belongs to one property — if property is deleted, units are deleted too
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='units'
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Unit number is the identifier within the property e.g. A1, B3, 101
    unit_number = models.CharField(max_length=20)

    floor = models.CharField(max_length=20, blank=True, null=True)
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)

    # Rent amount stored here is the current market rate for the unit
    # The lease will store the locked-in rate for each tenant
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='vacant'
    )

    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'units'
        ordering = ['unit_number']
        # Prevent duplicate unit numbers within the same property
        unique_together = ['property', 'unit_number']

    def __str__(self):
        return f'Unit {self.unit_number} — {self.property.name}'