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


class RevenueReportView(APIView):
    """Total revenue collected, broken down by month."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Total revenue from completed payments only
        total_revenue = Payment.objects.filter(
            status='completed'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        # Monthly revenue breakdown
        # TruncMonth groups payments by month
        monthly_revenue = Payment.objects.filter(
            status='completed'
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-month')

        # Format monthly data for frontend charts
        monthly_data = [
            {
                'month': entry['month'].strftime('%B %Y'),
                'total': float(entry['total']),
                'count': entry['count'],
            }
            for entry in monthly_revenue
        ]

        # Outstanding balances — pending invoices
        outstanding = RentInvoice.objects.filter(
            status='pending'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        # Overdue invoices
        overdue = RentInvoice.objects.filter(
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
    permission_classes = []

    def get(self, request):
        # Total units across all properties
        total_units = Unit.objects.count()

        # Occupied units
        occupied_units = Unit.objects.filter(status='occupied').count()

        # Vacant units
        vacant_units = Unit.objects.filter(status='vacant').count()

        # Units under maintenance
        maintenance_units = Unit.objects.filter(status='maintenance').count()

        # Occupancy rate as a percentage
        occupancy_rate = (
            (occupied_units / total_units * 100) if total_units > 0 else 0
        )

        # Per property breakdown
        properties = Property.objects.filter(is_active=True)
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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Payment counts by status
        total_payments = Payment.objects.count()
        completed_payments = Payment.objects.filter(status='completed').count()
        failed_payments = Payment.objects.filter(status='failed').count()
        pending_payments = Payment.objects.filter(status='pending').count()

        # Invoice counts by status
        total_invoices = RentInvoice.objects.count()
        paid_invoices = RentInvoice.objects.filter(status='paid').count()
        pending_invoices = RentInvoice.objects.filter(status='pending').count()
        overdue_invoices = RentInvoice.objects.filter(status='overdue').count()

        # Recent payments — last 10
        recent_payments = Payment.objects.filter(
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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Counts by status
        total = MaintenanceRequest.objects.count()
        pending = MaintenanceRequest.objects.filter(status='pending').count()
        assigned = MaintenanceRequest.objects.filter(status='assigned').count()
        in_progress = MaintenanceRequest.objects.filter(status='in_progress').count()
        completed = MaintenanceRequest.objects.filter(status='completed').count()

        # Counts by category
        by_category = MaintenanceRequest.objects.values(
            'category'
        ).annotate(
            count=Count('id')
        ).order_by('-count')

        # Counts by priority
        by_priority = MaintenanceRequest.objects.values(
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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Properties and units
        total_properties = Property.objects.filter(is_active=True).count()
        total_units = Unit.objects.count()
        occupied_units = Unit.objects.filter(status='occupied').count()
        occupancy_rate = (
            (occupied_units / total_units * 100) if total_units > 0 else 0
        )

        # Active leases
        active_leases = Lease.objects.filter(status='active').count()

        # Revenue
        total_revenue = Payment.objects.filter(
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Maintenance
        pending_maintenance = MaintenanceRequest.objects.filter(
            status='pending'
        ).count()

        # Pending invoices
        pending_invoices = RentInvoice.objects.filter(
            status='pending'
        ).count()

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
