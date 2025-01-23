from django.urls import path
from .views import (
    EmployeeOverviewAPIView, RemainingLeaveAPIView, 
    UpdateLeaveBalanceAPIView, EmployeeDashboardView, 
    AuthorizedDashboardView,EmployeeListAPIView,
)

urlpatterns = [
    path('api/employees/list/', EmployeeListAPIView.as_view(), name='employee-list'),
    path('api/employees/overview/', EmployeeOverviewAPIView.as_view(), name='employee_overview'),
    path('api/remaining-leave/', RemainingLeaveAPIView.as_view(), name='remaining_leave'),
    path('api/update-leave-balance/', UpdateLeaveBalanceAPIView.as_view(), name='update_leave_balance'),
    path('employee-dashboard/', EmployeeDashboardView.as_view(), name='employee_dashboard'),
    path('authorized-dashboard/', AuthorizedDashboardView.as_view(), name='authorized_dashboard'),
]