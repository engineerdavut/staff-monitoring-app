from django.core.cache import cache  
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from ..iattendancerepository import IAttendanceRepository
from employee.services import EmployeeService
from ..attendancecalculator import AttendanceCalculator
from employee_tracking_system.utils.time_utils import TimeCalculator
from employee.models import Employee
from ..models import Attendance  

import logging

logger = logging.getLogger(__name__)

class RealTimeUpdateService:
    def __init__(self, repository: IAttendanceRepository, employee_service: EmployeeService):
        self.repository = repository
        self.employee_service = employee_service
        self.channel_layer = get_channel_layer()

    def send_real_time_update_to_employee(self, employee: Employee, message: dict):
        group_name = f"user_{employee.id}_employee_attendance"
        try:
            async_to_sync(self.channel_layer.group_send)(
                group_name,
                {
                    'type': 'employee_realtime_attendance_update',
                    'message': message,
                    'id' : employee.id
                }
            )
            logger.info(f"Sent real-time update to {group_name}: {message}")
        except Exception as e:
            logger.error(f"Error sending real-time update to employee: {e}") 

    def send_real_time_update_to_authorized(self, message):
        group_name = 'authorized_attendance'
        try:
            async_to_sync(self.channel_layer.group_send)(
                group_name,
                {
                    'type': 'realtime_attendance_update',
                    'message': message
                }
            )
            logger.info(f"Sent real-time update to {group_name}: {message}")
        except Exception as e:
            logger.error(f"Error sending real-time update to authorized: {e}")
            
    def update_all_real_time_attendance(self, employee=None, now_local=None):
        try:
            if employee and now_local:
                self._send_single_employee_update(employee, now_local)

            else:
                now_utc = timezone.now()
                local_timezone = timezone.get_default_timezone()
                current_time_local = timezone.localtime(now_utc, local_timezone)
                today = current_time_local.date()
                
                employees = self.employee_service.get_all_employees()

                if not employees:
                    logger.info("update_all_real_time_attendance: No employees found.")
                    return

                for employee in employees:
                    self._send_single_employee_update(employee, current_time_local)


        except Exception as e:
            logger.error(f"Error during real-time update: {e}")
            raise
        
        
    def _send_single_employee_update(self, employee, current_time_local):
        today = current_time_local.date()
        attendances = self.repository.get_employee_attendances(employee.id, today)

        lateness = AttendanceCalculator.calculate_lateness(
            attendances=attendances,
            now=current_time_local,
            include_no_check_in=True
        )
        work_duration = AttendanceCalculator.calculate_work_duration(
            attendances=attendances,
            now=current_time_local
        )

        remaining_leave = employee.remaining_leave - lateness

        remaining_leave_display = self.employee_service.get_remaining_leave_displayy(employee, remaining_leave)

        status = Attendance.objects.determine_attendance_status(attendances, current_time_local, today)
        
        last_action_time = None
        if attendances:
            sorted_attendances = attendances.order_by('-check_out', '-check_in')
            last_attendance = sorted_attendances.first()
            last_action_time = last_attendance.check_out or last_attendance.check_in

        if last_action_time:
            last_action_time_display = last_action_time.strftime('%Y-%m-%d %H:%M')
        else:
            last_action_time_display = "N/A"

        message = {
            "remaining_leave": remaining_leave_display,
            "lateness": TimeCalculator.timedelta_to_hhmm(lateness),
            "work_duration": TimeCalculator.timedelta_to_hhmm(work_duration),
            "status": status,
            "last_action_time": last_action_time_display
        }
        self.send_real_time_update_to_employee(employee, message)

        authorized_message = {
            "id": employee.id,
            "remaining_leave": remaining_leave_display,
            "lateness": TimeCalculator.timedelta_to_hhmm(lateness),
            "work_duration": TimeCalculator.timedelta_to_hhmm(work_duration),
            "status": status,
            "last_action_time": last_action_time_display
        }
        self.send_real_time_update_to_authorized(authorized_message)

        logger.info(f"Real-time attendance update sent for employee {employee.id}.")