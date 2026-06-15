from django.urls import path
from .views import (
    RevenueReportView,
    OccupancyReportView,
    PaymentReportView,
    MaintenanceReportView,
    DashboardSummaryView,
)

urlpatterns = [
    # Individual reports
    path('reports/revenue/', RevenueReportView.as_view(), name='report-revenue'),
    path('reports/occupancy/', OccupancyReportView.as_view(), name='report-occupancy'),
    path('reports/payments/', PaymentReportView.as_view(), name='report-payments'),
    path('reports/maintenance/', MaintenanceReportView.as_view(), name='report-maintenance'),

    # Dashboard summary — all key metrics in one call
    path('reports/dashboard/', DashboardSummaryView.as_view(), name='report-dashboard'),
]