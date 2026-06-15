import uuid
from django.db import models
from accounts.models import TenantProfile
from properties.models import Unit


class MaintenanceRequest(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('emergency', 'Emergency'),
    )

    CATEGORY_CHOICES = (
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('structural', 'Structural'),
        ('appliances', 'Appliances'),
        ('security', 'Security'),
        ('cleaning', 'Cleaning'),
        ('other', 'Other'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Tenant who submitted the request
    tenant = models.ForeignKey(
        TenantProfile,
        on_delete=models.CASCADE,
        related_name='maintenance_requests'
    )

    # Unit derived automatically from tenant's active lease
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='maintenance_requests'
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    # Category helps landlord route the request to the right person
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other'
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Cloudinary URL for photo evidence of the issue
    image = models.ImageField(
        upload_to='maintenance_images/',
        blank=True,
        null=True
    )

    # Landlord notes — updated as work progresses
    landlord_notes = models.TextField(blank=True, null=True)

    # Timestamps for tracking how long requests take to resolve
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'maintenance_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.unit} — {self.status}'
