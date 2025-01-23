from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AttendanceViewSet, AttendanceStatusView, CheckInAPIView,CheckOutAPIView, DetailedMonthlyReportView , DetailedMonthlyWorkHoursAPIView

router = DefaultRouter()
router.register(r'attendances', AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('', include(router.urls)),
    path('status/', AttendanceStatusView.as_view(), name='attendance_status'),
    path('check-in/', CheckInAPIView.as_view(), name='check_in'),
    path('check-out/', CheckOutAPIView.as_view(), name='check_out'),
    path('detailed-monthly-report/', DetailedMonthlyReportView.as_view(), name='detailed_monthly_report'),
    path('monthly-report/<int:year>/<int:month>/', DetailedMonthlyWorkHoursAPIView.as_view(), name='monthly_report'),
]