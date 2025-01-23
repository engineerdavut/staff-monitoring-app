from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta, date
from employee.models import Employee
from ..models import Attendance
import logging

logger = logging.getLogger(__name__)

class AttendanceService:
    @transaction.atomic
    def set_employee_on_leave(self, employee: Employee, start_date: date, end_date: date):
        current_date = start_date
        while current_date <= end_date:
            try:
                attendance, created = Attendance.objects.get_or_create(
                    employee=employee,
                    date=current_date,
                    defaults={'status': 'on_leave'}
                )
                if not created:
                    if attendance.status != 'on_leave':
                        attendance.status = 'on_leave'
                        attendance.save()
                        logger.debug(f"Attendance updated to 'on_leave' for {employee.user.username} on {current_date}")
                logger.info(f"Set 'on_leave' for {employee.user.username} on {current_date}")
            except Exception as e:
                logger.error(f"Failed to set 'on_leave' for {employee.user.username} on {current_date}: {e}")
                raise ValidationError(f"Failed to set 'on_leave' for {current_date}: {e}")
            current_date += timedelta(days=1)