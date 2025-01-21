import logging
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .serializers import AttendanceSerializer
from .models import Attendance
from django.views.generic import TemplateView
from django.contrib.auth.models import AnonymousUser
from .utils import  get_check_in_out_service, get_attendance_report_service


logger = logging.getLogger(__name__)

class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or isinstance(user, AnonymousUser):
            return Attendance.objects.none()
        if user.user_type == 'authorized':
            return Attendance.objects.all()
        return Attendance.objects.filter(employee=user.employee)

class CheckInAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            check_in_out_service = get_check_in_out_service()
            employee = check_in_out_service.employee_service.get_employee(request.user.employee.id)
            if not employee:
                return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
            result = check_in_out_service.handle_check_in(employee)
            if 'error' in result:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(f"Error during check-in for user {request.user.username}: {str(e)}")
            return Response({"error": "Failed to check in. Please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CheckOutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            check_in_out_service = get_check_in_out_service()
            employee = check_in_out_service.employee_service.get_employee(request.user.employee.id)
            if not employee:
                return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
            result = check_in_out_service.handle_check_out(employee)
            if 'error' in result:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(f"Error during check-out for user {request.user.username}: {str(e)}")
            return Response({"error": "Failed to check out. Please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AttendanceStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            check_in_out_service = get_check_in_out_service()

            employee = check_in_out_service.employee_service.get_employee(request.user.employee.id)
            if not employee:
                return Response({"error": "Employee not found."}, status=404)

            # Get attendance status from service with include_no_check_in=True
            status_data = check_in_out_service.get_attendance_status(employee, include_no_check_in=True)

            logger.debug(f"Attendance status for {employee.user.username}: {status_data}")

            return Response(status_data)
        except Exception as e:
            logger.exception(f"Error fetching attendance status for {request.user.username}: {str(e)}")
            return Response({"error": "Failed to update attendance status. Please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DetailedMonthlyReportView(TemplateView):
    template_name = 'detailed_monthly_report.html'

class DetailedMonthlyWorkHoursAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, year, month):
        try:
            report_service = get_attendance_report_service()
            if request.user.user_type == 'authorized':
                report_data = report_service.get_monthly_report(year, month)
            else:
                employee = report_service.employee_service.get_employee(request.user.employee.id)
                report_data = [
                    report for report in report_service.get_monthly_report(year, month)
                    if report['employee'] == employee.user.username
                ]

            logger.debug(f"Report data: {report_data}")
            return Response(report_data, status=200)

        except Exception as e:
            logger.error(f"Error generating monthly report: {e}")
            return Response({'error': "Failed to generate monthly report."}, status=500)
