import uuid
from django.db import models
from leases.models import Lease


class RentInvoice(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Invoice belongs to a lease — one lease can have many invoices (monthly)
    lease = models.ForeignKey(
        Lease,
        on_delete=models.CASCADE,
        related_name='invoices'
    )

    # Amount due for this invoice period
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    due_date = models.DateField()

    # Stamp the date when payment is confirmed
    paid_date = models.DateField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Month and year this invoice covers e.g. June 2026
    invoice_month = models.PositiveIntegerField()
    invoice_year = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rent_invoices'
        ordering = ['-created_at']
        # Prevent duplicate invoices for same lease in same month
        unique_together = ['lease', 'invoice_month', 'invoice_year']

    def __str__(self):
        return f'Invoice — {self.lease} — {self.invoice_month}/{self.invoice_year}'


class Payment(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('mpesa', 'M-Pesa'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Payment is made against a specific invoice
    invoice = models.ForeignKey(
        RentInvoice,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='mpesa'
    )

    # Unique transaction code returned by the payment gateway
    transaction_code = models.CharField(max_length=100, unique=True, blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Phone number used for the payment
    phone_number = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f'Payment — {self.amount} — {self.status}'


class MpesaTransaction(models.Model):
    # Core fields 
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    checkout_request_id = models.CharField(max_length=100, blank=True)
    mpesa_receipt = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, default='Pending')

    # Links this transaction back to our internal Payment record
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name='mpesa_transaction',
        blank=True,
        null=True
    )

    # Raw response fields from Safaricom callback
    # result_code 0 = success, anything else = failure
    result_code = models.CharField(max_length=10, blank=True, null=True)
    result_desc = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mpesa_transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.phone_number} - {self.amount} - {self.status}'
