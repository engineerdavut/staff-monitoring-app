from django.urls import path
from .views import (
    EmployeeLeaveCreateAPIView,
    AuthorizedLeaveCreateAPIView,
    EmployeeLeaveListAPIView,
    AuthorizedLeaveListAPIView,
    LeaveActionAPIView,
    CancelLeaveAPIView
)

urlpatterns = [
    path('employee/create/', EmployeeLeaveCreateAPIView.as_view(), name='employee_leave_create'),
    path('authorized/create/', AuthorizedLeaveCreateAPIView.as_view(), name='authorized_leave_create'),
    path('employee/list/', EmployeeLeaveListAPIView.as_view(), name='employee_leave_list'),
    path('authorized/list/', AuthorizedLeaveListAPIView.as_view(), name='authorized_leave_list'),
    path('<int:pk>/<str:action>/', LeaveActionAPIView.as_view(), name='leave_action'),
    path('cancel/<int:pk>/', CancelLeaveAPIView.as_view(), name='cancel_leave'),
]