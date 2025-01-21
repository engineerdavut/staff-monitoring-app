import logging
from typing import List
from .iemployeerepository import IEmployeeRepository
from .models import Employee
from django.utils import timezone
from datetime import timedelta
from employee_tracking_system.utils.notification_utils import send_notification
from employee_tracking_system.utils.time_utils import TimeCalculator
from django.core.exceptions import ObjectDoesNotExist
from attendance.iattendancerepository import IAttendanceRepository
from .utils import get_attendance_repository,get_attendance_calculator, get_working_hours_service
from datetime import date  
from attendance.models import Attendance 
from django.db import transaction 


logger = logging.getLogger(__name__)

class EmployeeService:
    def __init__(self, repository: IEmployeeRepository, attendance_repository: IAttendanceRepository):
        self.repository = repository
        self.attendance_repository = attendance_repository
        self.attendance_calculator = get_attendance_calculator()
        self.working_hours_service = get_working_hours_service() 


    def get_employee(self, employee_id: int) -> Employee:
            try:
                employee = self.repository.get_employee(employee_id)  # Burada da employee ID kullanılmalı
                if not employee:
                    logger.warning(f"Employee not found for employee id {employee_id}")
                    return None
                return employee
            except ObjectDoesNotExist:
                logger.warning(f"Employee not found for employee id: {employee_id}")
                return None
            except Exception as e:
                logger.error(f"Error getting employee by id: {e}")
                return None

    def get_all_employees(self) -> List[Employee]:
        try:
            employees = self.repository.get_all_employees()
            logger.info(f"Retrieved all employees. Count: {len(employees)}")
            return employees
        except Exception as e:
            logger.error(f"Error retrieving all employees: {e}")
            return []
    @transaction.atomic
    def update_remaining_leave(self, employee: Employee, lateness: timedelta) -> None:
        try:
            employee.remaining_leave -= lateness

            # remaining_leave değerinin negatif olmamasını sağla
            if employee.remaining_leave < timedelta():
                employee.remaining_leave = timedelta()

            employee.save()
            logger.info(f"Leave balance updated for employee {employee.id} by lateness of {lateness}")

            # Düşük izin bakiyesi kontrolü (örneğin, 3 gün)
            if employee.remaining_leave <= timedelta(days=3):
                send_notification(
                    user=employee.user, 
                    notification_type="LOW_LEAVE_BALANCE", 
                    employee=employee.user.username, 
                    balance=self.get_remaining_leave_display(employee)
                )
        except Exception as e:
            logger.error(f"Error updating employee leave: {e}")

    @transaction.atomic
    def increment_total_lateness(self, employee: Employee, lateness: timedelta) -> None:
        try:
            employee.total_lateness += lateness
            employee.save()
            logger.info(f"Total lateness updated for employee {employee.id} by {lateness}")
        except Exception as e:
            logger.error(f"Error incrementing total lateness for employee {employee.id}: {e}")

    @transaction.atomic
    def increment_total_work_duration(self, employee: Employee, work_duration: timedelta) -> None:
        try:
            employee.total_work_duration += work_duration
            employee.save()
            logger.info(f"Total work duration updated for employee {employee.id} by {work_duration}")
        except Exception as e:
            logger.error(f"Error incrementing total work duration for employee {employee.id}: {e}")

    def get_authorized_employees(self) -> List[Employee]:
        try:
            return self.repository.get_authorized_employees()
        except Exception as e:
            logger.error(f"Error getting authorized employees: {e}")
            return []


    def reset_annual_leave(self, employee: Employee) -> None:
        try:
            employee.remaining_leave = timedelta(days=employee.annual_leave)
            employee.total_lateness = 0  # total_lateness artık int olduğu için 0 yapıyoruz
            employee.total_work_duration = timedelta()
            employee.save()
            logger.info(f"Annual leave reset for employee {employee.id}")
            send_notification(
                employee.user, 
                'LEAVE_BALANCE_UPDATED', 
                employee=employee.user.username, 
                balance=self.get_remaining_leave_display(employee)
            )
        except Exception as e:
            logger.error(f"Error resetting annual leave for employee {employee.id}: {e}")

    def get_remaining_leave_display(self, employee: Employee) -> str:
        try:
            remaining_leave = employee.remaining_leave
            days = remaining_leave.days
            hours, remainder = divmod(remaining_leave.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{days}d {hours}h {minutes}m"
        except Exception as e:
            logger.error(f"Error getting remaining leave display for employee {employee.id}: {e}")
            return "0d 0h 0m"


    def can_take_leave(self, employee: Employee, start_date, end_date) -> bool:
        try:
            from leave.services import LeaveService
            return LeaveService.can_employee_take_leave(employee, start_date, end_date)
        except Exception as e:
            logger.error(f"Error checking can take leave for employee {employee.id}: {e}")
            return False

    def get_remaining_leave_for_date(self, employee: Employee, date) -> int:
        try:
            current_year = timezone.now().year
            if date.year == current_year:
                return employee.remaining_leave.days
            elif date.year == current_year + 1:
                return employee.annual_leave
            else:
                return 0  # Gelecek yıllar için
        except Exception as e:
            logger.error(f"Error getting remaining leave for date: {e}")
            return 0
        
    def get_remaining_leave_displayy(self, employee: Employee, calculated_remaining_leave = None) -> str:
        try:
            if calculated_remaining_leave is None:
                remaining_leave = employee.remaining_leave
            else:
                remaining_leave = calculated_remaining_leave
            
            days = remaining_leave.days
            hours, remainder = divmod(remaining_leave.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{days}d {hours}h {minutes}m"
        except Exception as e:
            logger.error(f"Error getting remaining leave display for employee {employee.id}: {e}")
            return "0d 0h 0m"

    @transaction.atomic
    def update_leave_balance(self, employee: Employee, change: int) -> None:
        try:
            # remaining_leave bir DurationField olduğu için timedelta ekliyoruz
            employee.remaining_leave += timedelta(days=change)
            
            # annual_leave bir IntegerField olduğu için doğrudan integer ekliyoruz
            employee.annual_leave += change

            # remaining_leave değerinin negatif olmamasını sağla
            if employee.remaining_leave < timedelta():
                employee.remaining_leave = timedelta()

            employee.save()
            logger.info(f"Leave balance updated for employee {employee.id} by {change} days")

            # Düşük izin bakiyesi kontrolü (örneğin, 3 gün)
            if employee.remaining_leave <= timedelta(days=3):
                send_notification(
                    user=employee.user, 
                    notification_type="LOW_LEAVE_BALANCE", 
                    employee=employee.user.username, 
                    balance=self.get_remaining_leave_display(employee)
                )
            
            # Authorized user’lara da bildirim
            authorized_employees = self.get_authorized_employees()
            for auth_employee in authorized_employees:
                send_notification(
                    auth_employee.user, 
                    'LEAVE_BALANCE_UPDATED', 
                    employee=employee.user.username, 
                    balance=self.get_remaining_leave_display(employee)
                )
        except Exception as e:
            logger.error(f"Error updating leave balance: {e}")

    def get_employees_with_low_leave_balance(self, threshold_days: int) -> List[Employee]:
        try:
            threshold = timedelta(days=threshold_days)
            return self.repository.get_employees_with_low_leave(threshold=threshold)
        except Exception as e:
            logger.error(f"Error getting employees with low leave balance: {e}")
            return []

    def get_employees_without_check_in(self, target_date) -> List[Employee]:
        try:
            return self.repository.get_employees_without_attendance(target_date)
        except Exception as e:
            logger.error(f"Error getting employees without check in: {e}")
            return []
        
    def get_daily_attendance_summary(self, employee: Employee, target_date: date) -> dict:
        try:
            now = timezone.now()
            logger.debug(f"Fetching attendances for employee_id={employee.id} on date={target_date}")
            attendances = self.attendance_repository.get_employee_attendances(employee.id, target_date)
            logger.debug(f"Attendances fetched: {attendances.count()} records")

            status = Attendance.objects.determine_attendance_status(attendances, now, target_date)
            logger.debug(f"Determined status: {status}")

            daily_lateness = self.attendance_calculator.calculate_lateness(
                attendances=attendances,
                now=now,
                include_no_check_in=True
            )
            logger.debug(f"Calculated daily lateness: {daily_lateness}")

            daily_work = self.attendance_calculator.calculate_work_duration(
                attendances=attendances,
                now=now
            )
            logger.debug(f"Calculated daily work duration: {daily_work}")

            last_attendance = attendances.order_by('-check_out', '-check_in').first()
            last_action_time = last_attendance.check_out or last_attendance.check_in if last_attendance else None
            logger.debug(f"Last action time: {last_action_time}")

            summary = {
                "id": employee.id,
                "username": employee.user.username,
                "status": status,
                "last_action_time": TimeCalculator.format_datetime(last_action_time),
                "lateness": TimeCalculator.timedelta_to_hhmm(daily_lateness),
                "work_duration": TimeCalculator.timedelta_to_hhmm(daily_work),
                "remaining_leave": self.get_remaining_leave_display(employee),
                "annual_leave": employee.annual_leave
            }
            logger.debug(f"Summary for employee_id={employee.id}: {summary}")
            return summary
        except Exception as e:
            logger.error(f"Error in get_daily_attendance_summary for employee_id={employee.id}: {e}")
            return {
                "id": employee.id,
                "username": employee.user.username if employee and employee.user else "N/A",
                "status": "N/A",
                "last_action_time": "N/A",
                "lateness": "0m",
                "work_duration": "0m",
                "remaining_leave": self.get_remaining_leave_display(employee) if employee else "0d 0h 0m",
                "annual_leave": employee.annual_leave if employee else 0
            }