from rest_framework import serializers
from .models import RentInvoice, Payment, MpesaTransaction


class RentInvoiceSerializer(serializers.ModelSerializer):
    # Human readable status
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Lease details for display
    tenant_name = serializers.CharField(
        source='lease.tenant.user.full_name',
        read_only=True
    )
    unit_number = serializers.CharField(
        source='lease.unit.unit_number',
        read_only=True
    )
    property_name = serializers.CharField(
        source='lease.unit.property.name',
        read_only=True
    )

    class Meta:
        model = RentInvoice
        fields = [
            'id',
            'lease',
            'tenant_name',
            'unit_number',
            'property_name',
            'amount',
            'due_date',
            'paid_date',
            'status',
            'status_display',
            'invoice_month',
            'invoice_year',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'paid_date', 'created_at', 'updated_at']


class PaymentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id',
            'invoice',
            'amount',
            'payment_method',
            'payment_method_display',
            'transaction_code',
            'status',
            'status_display',
            'phone_number',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'transaction_code', 'status', 'created_at', 'updated_at']


class MpesaTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = MpesaTransaction
        fields = [
            'id',
            'payment',
            'phone_number',
            'amount',
            'checkout_request_id',
            'mpesa_receipt',
            'result_code',
            'result_desc',
            'status',
            'created_at',
        ]
        read_only_fields = fields