import uuid
from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import TenantProfile
from properties.models import Unit

User = get_user_model()


class Lease(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),      #  ADDED: Tenant applied, waiting for landlord
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Lease links a tenant to a specific unit
    tenant = models.ForeignKey(
        TenantProfile,
        on_delete=models.PROTECT,
        related_name='leases'
    )

    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name='leases'
    )

    # Rent amount locked in at the time of signing
    # This preserves historical accuracy even if unit rent changes later
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Security deposit collected at lease signing
    deposit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    start_date = models.DateField()

    # end_date is nullable — some leases are open-ended month to month
    end_date = models.DateField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'  # CHANGED: Default is now 'pending' instead of 'active'
    )

    # Additional terms or notes for this specific lease
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leases'
        ordering = ['-created_at']

    def __str__(self):
        return f'Lease — {self.tenant.user.full_name} in {self.unit}'

    def save(self, *args, **kwargs):
        # Get the existing lease status before saving if this is an update
        if self.pk:
            try:
                old_lease = Lease.objects.get(pk=self.pk)
                old_status = old_lease.status
            except Lease.DoesNotExist:
                old_status = None
        else:
            old_status = None

        # Save the lease first
        super().save(*args, **kwargs)

        # Update unit status based on lease status
        # This is the business rule that lives in the model layer
        if self.status == 'active':
            # When lease is active, mark the unit as occupied
            self.unit.status = 'occupied'
            self.unit.save()
        elif self.status in ['expired', 'terminated']:
            # When lease ends, check if there are other active leases on this unit
            # before marking it as vacant
            other_active_leases = Lease.objects.filter(
                unit=self.unit,
                status='active'
            ).exclude(pk=self.pk).exists()

            if not other_active_leases:
                # No other active leases — mark unit as vacant
                self.unit.status = 'vacant'
                self.unit.save()
        # 👈 ADDED: 'pending' status does NOT change unit status
        # Unit remains vacant until the lease becomes active


class LeaseTerminationRequest(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # The lease this termination request is against
    lease = models.ForeignKey(
        Lease,
        on_delete=models.CASCADE,
        related_name='termination_requests'
    )

    # The tenant user who submitted the request
    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='termination_requests_made'
    )

    # Why the tenant wants to leave early
    reason = models.TextField()

    # The date the tenant wants to vacate
    requested_vacate_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Deposit is always non-refundable on early termination
    # This flag is set to True automatically on creation and cannot be changed
    deposit_forfeited = models.BooleanField(default=True)

    # Auto-generated system note about deposit forfeiture
    # Visible to the tenant so they are fully aware before submitting
    deposit_note = models.TextField(blank=True)

    # Who reviewed this request — landlord or admin
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='termination_requests_reviewed'
    )

    # When the review happened
    reviewed_at = models.DateTimeField(null=True, blank=True)

    # Optional note from the landlord/admin when approving or rejecting
    review_note = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lease_termination_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f'TerminationRequest — {self.lease} — {self.status}'

    def save(self, *args, **kwargs):
        # Auto-generate the deposit forfeiture note on first creation
        if not self.pk and not self.deposit_note:
            amount = self.lease.deposit_amount
            self.deposit_note = (
                f"Your security deposit of KES {amount:,.2f} is non-refundable "
                f"as this lease is being terminated early at your request. "
                f"Any outstanding rent invoices must be settled before this "
                f"request can be approved."
            )
        super().save(*args, **kwargs)