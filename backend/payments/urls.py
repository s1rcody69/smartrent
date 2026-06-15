from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RentInvoiceViewSet,
    PaymentViewSet,
    MpesaSTKPushView,
    MpesaCallbackView,
)

# Router handles standard CRUD endpoints automatically
router = DefaultRouter()
router.register(r'invoices', RentInvoiceViewSet, basename='invoice')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),

    # STK Push — tenant initiates payment (equivalent to teacher's pay/ view)
    path('payments/mpesa/stk-push/', MpesaSTKPushView.as_view(), name='mpesa-stk-push'),

    # Callback — Safaricom posts result here (matches teacher's api/mpesa/callback/)
    path('payments/mpesa/callback/', MpesaCallbackView.as_view(), name='mpesa-callback'),
]