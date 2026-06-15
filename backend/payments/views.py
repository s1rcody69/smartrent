import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone

from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import RentInvoice, Payment, MpesaTransaction
from .serializers import RentInvoiceSerializer, PaymentSerializer
from .mpesa import initiate_stk_push


def format_phone(phone):
    """Normalize any common Kenyan format to 2547XXXXXXXX."""
    
    phone = phone.strip().replace('+', '')
    if phone.startswith('0'):
        phone = '254' + phone[1:]
    elif phone.startswith('7') or phone.startswith('1'):
        phone = '254' + phone
    return phone


class RentInvoiceViewSet(viewsets.ModelViewSet):
    # CRUD for rent invoices
    serializer_class = RentInvoiceSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'lease', 'invoice_month', 'invoice_year']
    ordering_fields = ['due_date', 'created_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        return RentInvoice.objects.all()


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    # Payments are read-only — created through STK Push only
    serializer_class = PaymentSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'invoice']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        return Payment.objects.all()


class MpesaSTKPushView(APIView):
    """Start the payment — adapted from teacher's pay() view for REST API."""
    permission_classes = []

    def post(self, request):
        # Get and normalize phone number 
        phone = format_phone(request.data.get('phone_number', ''))
        amount = request.data.get('amount')
        invoice_id = request.data.get('invoice_id')

        if not phone or not amount or not invoice_id:
            return Response(
                {'error': 'phone_number, amount and invoice_id are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the invoice
        try:
            invoice = RentInvoice.objects.get(id=invoice_id)
        except RentInvoice.DoesNotExist:
            return Response(
                {'error': 'Invoice not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check invoice is not already paid
        if invoice.status == 'paid':
            return Response(
                {'error': 'This invoice has already been paid.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Initiate STK Push using initiate_stk_push function
        response = initiate_stk_push(
            phone_number=phone,
            amount=amount,
            account_reference=f'SmartRent-{str(invoice_id)[:8]}'
        )

        # Save a pending record we can update when the callback arrives
        #  MpesaTransaction.objects.create() logic
        if response.get('ResponseCode') == '0':
            # Create internal payment record
            payment = Payment.objects.create(
                invoice=invoice,
                amount=amount,
                payment_method='mpesa',
                phone_number=phone,
                status='pending'
            )

            # Create M-Pesa transaction record
            MpesaTransaction.objects.create(
                payment=payment,
                phone_number=phone,
                amount=amount,
                checkout_request_id=response.get('CheckoutRequestID', ''),
                status='Pending',
            )

            return Response({
                'message': 'Check your phone and enter your M-Pesa PIN.',
                'checkout_request_id': response.get('CheckoutRequestID'),
                'payment_id': str(payment.id),
            }, status=status.HTTP_200_OK)

        return Response(
            {'error': 'Could not initiate payment. Try again.', 'details': response},
            status=status.HTTP_400_BAD_REQUEST
        )


@method_decorator(csrf_exempt, name='dispatch')
class MpesaCallbackView(APIView):
    """Receive the payment result from Daraja.
    Logic taken directly from teacher's mpesa_callback() view."""
    permission_classes = []

    def post(self, request):
        # Parse the callback data from Safaricom
        data = request.data
        callback = data.get('Body', {}).get('stkCallback', {})
        checkout_id = callback.get('CheckoutRequestID')
        result_code = callback.get('ResultCode')

        # Find the matching transaction
        try:
            transaction = MpesaTransaction.objects.get(
                checkout_request_id=checkout_id
            )
        except MpesaTransaction.DoesNotExist:
            # Always acknowledge even if we cannot find the transaction
            return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})

        if result_code == 0:
            # Payment succeeded — pull the receipt from the metadata
            items = callback.get('CallbackMetadata', {}).get('Item', [])
            receipt = next(
                (i['Value'] for i in items if i['Name'] == 'MpesaReceiptNumber'),
                '',
            )

            transaction.mpesa_receipt = receipt
            transaction.status = 'Completed'
            transaction.save()

            # Update the linked payment record
            if transaction.payment:
                transaction.payment.status = 'completed'
                transaction.payment.transaction_code = receipt
                transaction.payment.save()

                # Mark the invoice as paid
                invoice = transaction.payment.invoice
                invoice.status = 'paid'
                invoice.paid_date = timezone.now().date()
                invoice.save()

        else:
            # Non-zero code means cancelled, timed out, or failed
            transaction.status = 'Failed'
            transaction.save()

            if transaction.payment:
                transaction.payment.status = 'failed'
                transaction.payment.save()

        # Always acknowledge receipt so Daraja stops retrying
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
