from .models import Leave
from .ileaverepository import ILeaveRepository
from .managers import LeaveManager
from employee.models import Employee 
from datetime import date
from typing import List
import logging
from rest_framework.exceptions import ValidationError
from datetime import timedelta 
from django.db.models import QuerySet  
from django.utils import timezone 


logger = logging.getLogger(__name__)

class LeaveRepository(ILeaveRepository):
    def __init__(self):
        self.manager = LeaveManager()

    def get_leave(self, leave_id: int) -> Leave:
        try:
            return Leave.objects.get(id=leave_id)
        except Leave.DoesNotExist:
            logger.error(f"Leave with ID {leave_id} does not exist.")
            return None

    def get_employee_leaves(self, employee: Employee) -> List[Leave]:
        return list(Leave.objects.filter(employee=employee))

    def get_all_leaves(self) -> List[Leave]:
        return list(Leave.objects.all())

    def create_leave(self, leave_data: dict) -> Leave:
        leave = Leave.objects.create(**leave_data)
        logger.info(f"Leave created: {leave}")
        return leave

    def update_leave(self, leave: Leave) -> Leave:
        leave.save()
        logger.info(f"Leave updated: {leave}")
        return leave

    def get_overlapping_leaves(self, employee: Employee, start_date: date, end_date: date) -> QuerySet:
        overlapping = Leave.objects.filter(
            employee=employee,
            status__in=[Leave.PENDING, Leave.APPROVED],
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        return overlapping  

    def calculate_leave_days(self, start_date: date, end_date: date, holidays: List[date] = None) -> int:
        leave_days = self.manager.calculate_leave_days(start_date, end_date, holidays)
        logger.debug(f"Calculated leave days from {start_date} to {end_date}: {leave_days}")
        return leave_days

    def get_remaining_leave(self, employee: Employee) -> int:
        remaining = employee.remaining_leave.days  # .days attribute'u ile gün sayısını alın
        logger.debug(f"Employee {employee.user.username} remaining leave: {remaining}")
        return remaining

    def update_remaining_leave(self, employee: Employee, leave_days: int) -> int:
        if leave_days > employee.remaining_leave.days:
            logger.error(f"Employee {employee.user.username} does not have enough remaining leave. Requested: {leave_days}, Available: {employee.remaining_leave.days}")
            raise ValidationError("Not enough leave days available.")
        employee.remaining_leave -= timedelta(days=leave_days)
        employee.save()
        logger.info(f"Employee {employee.user.username} remaining leave updated to {employee.remaining_leave.days}")
        return employee.remaining_leave.days

    def update_leave_status(self, leave_id, new_status):
        try:
            leave = Leave.objects.get(id=leave_id)
            Leave.objects.filter(id=leave_id).update(status=new_status, updated_at=timezone.now())
            return Leave.objects.get(id=leave_id)
        except Leave.DoesNotExist:
            return None