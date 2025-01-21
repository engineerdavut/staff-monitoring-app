
from typing import List, Any
from datetime import date, timedelta
from .models import Attendance
from .iattendancerepository import IAttendanceRepository
from employee.models import Employee
from .attendancecalculator import AttendanceCalculator
from employee_tracking_system.services.working_hours_service import WorkingHoursService
from django.utils import timezone
from django.db.models import QuerySet
import logging

logger = logging.getLogger(__name__)

from django.apps import apps

class AttendanceRepository(IAttendanceRepository):
    def get_employee_attendances(self, employee_id: int, target_date: date) -> QuerySet[Attendance]:
        try:
            return Attendance.objects.filter(employee_id=employee_id, date=target_date)
        except Exception as e:
            logger.error(f"Error getting attendances for employee {employee_id} on {target_date}: {e}")
            return Attendance.objects.none()

    def get_all_attendances_between_dates(self, start_date: date, end_date: date) -> List['Attendance']:
        Attendance = apps.get_model('attendance', 'Attendance')
        return Attendance.objects.filter(date__range=(start_date, end_date)).select_related('employee')

    def create_attendance(self, data: dict) -> 'Attendance':
        Attendance = apps.get_model('attendance', 'Attendance')
        return Attendance.objects.create(**data)

    def get_checked_out_attendances(self, date: date) -> List['Attendance']:
        Attendance = apps.get_model('attendance', 'Attendance')
        return Attendance.objects.filter(date=date, check_out__isnull=False).select_related('employee')

    def get_late_attendances(self, date: date) -> List['Attendance']:
        Attendance = apps.get_model('attendance', 'Attendance')
        return Attendance.objects.filter(date=date, check_in__isnull=False, lateness__gt=0).select_related('employee')

    def calculate_employee_lateness(self, employee: Employee, date: date) -> timedelta:
        attendances = self.get_employee_attendances(employee.id, date)
        now = timezone.now()
        return AttendanceCalculator.calculate_lateness(attendances, now, include_no_check_in=True)

    def is_employee_on_leave(self, employee_id: int, date: date) -> bool:
        Attendance = apps.get_model('attendance', 'Attendance')
        return Attendance.objects.filter(employee_id=employee_id, date=date, status='on_leave').exists()

    def get_authorized_employees(self) -> List[Employee]:
        return Employee.objects.filter(user__is_staff=True)