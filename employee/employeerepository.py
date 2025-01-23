from typing import List, Optional
from datetime import date, timedelta
from .models import Employee
from .iemployeerepository import IEmployeeRepository
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)


class EmployeeRepository(IEmployeeRepository):
    def get_employee(self, employee_id: int) -> Optional[Employee]:
            try:
                return Employee.objects.get(id=employee_id) 
            except ObjectDoesNotExist:
                logger.warning(f"Employee not found for employee id: {employee_id}")
                return None
            except Exception as e:
                logger.error(f"Error getting employee with id {employee_id}: {e}")
                return None


    def get_all_employees(self) -> List[Employee]:
        try:
            return Employee.objects.all()
        except Exception as e:
            logger.error(f"Error getting all employee: {e}")
            return []

    def get_employees_without_checkin(self, target_date: date) -> List[Employee]:
        try:
            return Employee.objects.exclude(
                attendance__date=target_date
            ).distinct()
        except Exception as e:
            logger.error(f"Error getting employees without check in: {e}")
            return []

    def get_authorized_employees(self) -> List[Employee]:
        try:
             return Employee.objects.filter(user__user_type='authorized')
        except Exception as e:
             logger.error(f"Error getting authorized employees: {e}")
             return []

    def get_employees_with_low_leave_balance(self, threshold_days: int) -> List[Employee]:
        try:
            threshold = timedelta(days=threshold_days)
            return Employee.objects.filter(remaining_leave__lte=threshold)
        except Exception as e:
            logger.error(f"Error getting employees with low leave balance: {e}")
            return []

    def update_employee_leave(self, employee: Employee, lateness: str) -> None:
       try:
          lateness_hours, lateness_minutes = map(int, lateness.split(':'))
          total_lateness_timedelta = timedelta(hours=lateness_hours, minutes=lateness_minutes)
          employee.total_lateness += total_lateness_timedelta
          full_days = employee.total_lateness.total_seconds() // (24 * 60 * 60)
          if full_days > 0:
            employee.remaining_leave = max(0, employee.remaining_leave - int(full_days))
            employee.total_lateness -= timedelta(days=int(full_days))
          employee.save()
          logger.info(f"Employee leave updated {employee.id} by {lateness}")
       except Exception as e:
            logger.error(f"Error updating employee leave: {e}")

    def update_employee_total_lateness(self,employee: Employee, lateness: timedelta, work_duration:timedelta) -> None:
        try:
           employee.total_lateness += lateness
           employee.total_work_duration += work_duration
           employee.save()
           logger.info(f"Total lateness and work duration updated for employee {employee.id}")
        except Exception as e:
           logger.error(f"Error updating total lateness and work duration for employee {employee.id}: {e}")
    
    def get_employees_without_attendance(self, date):
        return Employee.objects.exclude(
            attendance__date=date,
            attendance__check_in__isnull=False
        ).distinct()

    def get_employees_with_low_leave(self, threshold_days=3):
        return Employee.objects.filter(remaining_leave__lt=timedelta(days=threshold_days))