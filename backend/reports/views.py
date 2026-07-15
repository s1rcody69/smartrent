from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status

from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncMonth

from payments.models import Payment, RentInvoice
from properties.models import Property, Unit
from leases.models import Lease
from maintenance.models import MaintenanceRequest
from accounts.models import LandlordProfile


class IsAdminOrLandlord(permissions.BasePermission):
    # Reports expose aggregate platform/business data —
    # tenants have no legitimate reason to see revenue or occupancy totals
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('admin', 'landlord')


class RevenueReportView(APIView):
    """Total revenue collected, broken down by month."""
    permission_classes = [IsAdminOrLandlord]

    def get(self, request):
        user = request.user
        
        # Base queryset - filter by landlord if not admin
        if user.role == 'admin':
            payments = Payment.objects.filter(status='completed')
            invoices = RentInvoice.objects.all()
        else:
            # Landlord: only see payments from their properties
            try:
                landlord_profile = user.landlord_profile
                payments = Payment.objects.filter(
                    status='completed',
                    invoice__lease__unit__property__landlord=landlord_profile
                )
                invoices = RentInvoice.objects.filter(
                    lease__unit__property__landlord=landlord_profile
                )
            except LandlordProfile.DoesNotExist:
                payments = Payment.objects.none()
                invoices = RentInvoice.objects.none()

        # Total revenue from completed payments only
        total_revenue = payments.aggregate(
            total=Sum('amount')
        )['total'] or 0

        # Monthly revenue breakdown
        monthly_revenue = payments.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-month')

        monthly_data = [
            {
                'month': entry['month'].strftime('%B %Y'),
                'total': float(entry['total']),
                'count': entry['count'],
            }
            for entry in monthly_revenue
        ]

        # Outstanding balances — pending invoices
        outstanding = invoices.filter(
            status='pending'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        # Overdue invoices
        overdue = invoices.filter(
            status='overdue'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        return Response({
            'total_revenue': float(total_revenue),
            'outstanding_balance': float(outstanding),
            'overdue_balance': float(overdue),
            'monthly_breakdown': monthly_data,
        })


class OccupancyReportView(APIView):
    """Occupancy rate across all properties."""
    permission_classes = [IsAdminOrLandlord]

    def get(self, request):
        user = request.user

        # Base querysets - filter by landlord if not admin
        if user.role == 'admin':
            units = Unit.objects.all()
            properties = Property.objects.filter(is_active=True)
        else:
            try:
                landlord_profile = user.landlord_profile
                units = Unit.objects.filter(property__landlord=landlord_profile)
                properties = Property.objects.filter(
                    landlord=landlord_profile,
                    is_active=True
                )
            except LandlordProfile.DoesNotExist:
                units = Unit.objects.none()
                properties = Property.objects.none()

        total_units = units.count()
        occupied_units = units.filter(status='occupied').count()
        vacant_units = units.filter(status='vacant').count()
        maintenance_units = units.filter(status='maintenance').count()

        occupancy_rate = (
            (occupied_units / total_units * 100) if total_units > 0 else 0
        )

        # Per property breakdown
        property_breakdown = []
        for prop in properties:
            prop_total = prop.units.count()
            prop_occupied = prop.units.filter(status='occupied').count()
            prop_rate = (prop_occupied / prop_total * 100) if prop_total > 0 else 0

            property_breakdown.append({
                'property_id': str(prop.id),
                'property_name': prop.name,
                'city': prop.city,
                'total_units': prop_total,
                'occupied_units': prop_occupied,
                'vacant_units': prop_total - prop_occupied,
                'occupancy_rate': round(prop_rate, 2),
            })

        return Response({
            'total_units': total_units,
            'occupied_units': occupied_units,
            'vacant_units': vacant_units,
            'maintenance_units': maintenance_units,
            'occupancy_rate': round(occupancy_rate, 2),
            'property_breakdown': property_breakdown,
        })


class PaymentReportView(APIView):
    """Payment history and summary statistics."""
    permission_classes = [IsAdminOrLandlord]

    def get(self, request):
        user = request.user

        # Base querysets - filter by landlord if not admin
        if user.role == 'admin':
            payments = Payment.objects.all()
            invoices = RentInvoice.objects.all()
        else:
            try:
                landlord_profile = user.landlord_profile
                payments = Payment.objects.filter(
                    invoice__lease__unit__property__landlord=landlord_profile
                )
                invoices = RentInvoice.objects.filter(
                    lease__unit__property__landlord=landlord_profile
                )
            except LandlordProfile.DoesNotExist:
                payments = Payment.objects.none()
                invoices = RentInvoice.objects.none()

        # Payment counts by status
        total_payments = payments.count()
        completed_payments = payments.filter(status='completed').count()
        failed_payments = payments.filter(status='failed').count()
        pending_payments = payments.filter(status='pending').count()

        # Invoice counts by status
        total_invoices = invoices.count()
        paid_invoices = invoices.filter(status='paid').count()
        pending_invoices = invoices.filter(status='pending').count()
        overdue_invoices = invoices.filter(status='overdue').count()

        # Recent payments — last 10
        recent_payments = payments.filter(
            status='completed'
        ).order_by('-created_at')[:10].values(
            'id',
            'amount',
            'phone_number',
            'transaction_code',
            'created_at',
            'invoice__lease__tenant__user__first_name',
            'invoice__lease__tenant__user__last_name',
            'invoice__lease__unit__unit_number',
            'invoice__lease__unit__property__name',
        )

        return Response({
            'payments': {
                'total': total_payments,
                'completed': completed_payments,
                'failed': failed_payments,
                'pending': pending_payments,
            },
            'invoices': {
                'total': total_invoices,
                'paid': paid_invoices,
                'pending': pending_invoices,
                'overdue': overdue_invoices,
            },
            'recent_payments': list(recent_payments),
        })


class MaintenanceReportView(APIView):
    """Maintenance request statistics."""
    permission_classes = [IsAdminOrLandlord]

    def get(self, request):
        user = request.user

        # Base queryset - filter by landlord if not admin
        if user.role == 'admin':
            requests = MaintenanceRequest.objects.all()
        else:
            try:
                landlord_profile = user.landlord_profile
                requests = MaintenanceRequest.objects.filter(
                    unit__property__landlord=landlord_profile
                )
            except LandlordProfile.DoesNotExist:
                requests = MaintenanceRequest.objects.none()

        # Counts by status
        total = requests.count()
        pending = requests.filter(status='pending').count()
        assigned = requests.filter(status='assigned').count()
        in_progress = requests.filter(status='in_progress').count()
        completed = requests.filter(status='completed').count()

        # Counts by category
        by_category = requests.values(
            'category'
        ).annotate(
            count=Count('id')
        ).order_by('-count')

        # Counts by priority
        by_priority = requests.values(
            'priority'
        ).annotate(
            count=Count('id')
        ).order_by('-count')

        return Response({
            'total_requests': total,
            'by_status': {
                'pending': pending,
                'assigned': assigned,
                'in_progress': in_progress,
                'completed': completed,
            },
            'by_category': list(by_category),
            'by_priority': list(by_priority),
        })


class DashboardSummaryView(APIView):
    """Single endpoint that returns all key metrics for the dashboard."""
    permission_classes = [IsAdminOrLandlord]

    def get(self, request):
        user = request.user

        # Base querysets - filter by landlord if not admin
        if user.role == 'admin':
            properties = Property.objects.filter(is_active=True)
            units = Unit.objects.all()
            leases = Lease.objects.filter(status='active')
            payments = Payment.objects.filter(status='completed')
            maintenance = MaintenanceRequest.objects.filter(status='pending')
            invoices = RentInvoice.objects.filter(status='pending')
        else:
            try:
                landlord_profile = user.landlord_profile
                properties = Property.objects.filter(
                    landlord=landlord_profile,
                    is_active=True
                )
                units = Unit.objects.filter(property__landlord=landlord_profile)
                leases = Lease.objects.filter(
                    status='active',
                    unit__property__landlord=landlord_profile
                )
                payments = Payment.objects.filter(
                    status='completed',
                    invoice__lease__unit__property__landlord=landlord_profile
                )
                maintenance = MaintenanceRequest.objects.filter(
                    status='pending',
                    unit__property__landlord=landlord_profile
                )
                invoices = RentInvoice.objects.filter(
                    status='pending',
                    lease__unit__property__landlord=landlord_profile
                )
            except LandlordProfile.DoesNotExist:
                properties = Property.objects.none()
                units = Unit.objects.none()
                leases = Lease.objects.none()
                payments = Payment.objects.none()
                maintenance = MaintenanceRequest.objects.none()
                invoices = RentInvoice.objects.none()

        total_properties = properties.count()
        total_units = units.count()
        occupied_units = units.filter(status='occupied').count()
        occupancy_rate = (
            (occupied_units / total_units * 100) if total_units > 0 else 0
        )

        active_leases = leases.count()
        total_revenue = payments.aggregate(total=Sum('amount'))['total'] or 0
        pending_maintenance = maintenance.count()
        pending_invoices = invoices.count()

        return Response({
            'total_properties': total_properties,
            'total_units': total_units,
            'occupied_units': occupied_units,
            'occupancy_rate': round(occupancy_rate, 2),
            'active_leases': active_leases,
            'total_revenue': float(total_revenue),
            'pending_maintenance': pending_maintenance,
            'pending_invoices': pending_invoices,
        })
