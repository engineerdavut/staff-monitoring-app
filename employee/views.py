from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.views.generic import TemplateView
from .services import EmployeeService
from .serializers import EmployeeSerializer,EmployeeOverviewSerializer,EmployeeListSerializer
from .utils import get_employee_service
from django.utils import timezone 
from .employeerepository import EmployeeRepository
from rest_framework import status  
from attendance.attendancerepository import AttendanceRepository
from .models import Employee
 
import logging

logger = logging.getLogger(__name__)

class EmployeeOverviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            employee_service = get_employee_service() 
            today = timezone.localtime(timezone.now()).date()

            if request.user.user_type == 'authorized':
                employees = employee_service.get_all_employees()
            else:
                employee = employee_service.get_employee(request.user.employee.id)
                if not employee:
                    return Response({"error": "Employee not found"}, status=404)
                employees = [employee]

            overview_data = []
            for emp in employees:
                if emp is None:
                    logger.warning(f"Employee is None for user id {request.user.employee.id}")
                    continue
                summary = employee_service.get_daily_attendance_summary(emp, today)
                overview_data.append(summary)

            serializer = EmployeeOverviewSerializer(overview_data, many=True)
            logger.debug(f"Serialized overview data: {serializer.data}")
            return Response(serializer.data, status=200)

        except Exception as e:
            logger.error(f"Error in EmployeeOverviewAPIView: {str(e)}")
            return Response({"error": "An unexpected error occurred"}, status=500)

class EmployeeListAPIView(generics.ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeListSerializer
    permission_classes = [IsAuthenticated]

class RemainingLeaveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            employee_service = get_employee_service()
            employee = employee_service.get_employee(request.user.employee.id)
            if not employee:
                return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = EmployeeSerializer(employee, context={'service': employee_service})
            return Response({"remaining_leave": serializer.data['remaining_leave_display']})
        except Exception as e:
            logger.error(f"Error in RemainingLeaveAPIView: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateLeaveBalanceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        employee_id = request.data.get('employee_id')
        change = request.data.get('change')

        if employee_id is None or change is None:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            employee_service = get_employee_service()
            employee = employee_service.get_employee(employee_id)
            if not employee:
                return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
            employee_service.update_leave_balance(employee, int(change))
            logger.info(f"Leave balance updated for employee {employee_id} by {change} days")
            return Response({"success": True, "message": "Leave balance updated successfully"})
        except ValueError:
            logger.error(f"Invalid change value: {change}")
            return Response({"error": "Invalid change value"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating leave balance: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmployeeDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            repository = EmployeeRepository()
            attendance_repository = AttendanceRepository()
            service = EmployeeService(repository, attendance_repository)
            employee = service.get_employee(pk)
            if not employee:
                return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = EmployeeSerializer(employee, context={'service': service})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in EmployeeDetailAPIView: {str(e)}")
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmployeeDashboardView(TemplateView):
    template_name = 'employee_dashboard.html'

class AuthorizedDashboardView(TemplateView):
    template_name = 'authorized_dashboard.html'