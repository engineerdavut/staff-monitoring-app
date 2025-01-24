from django.utils import timezone
from django.db import transaction
from django.apps import apps
from django.core.cache import cache  
from ..attendancerepository import AttendanceRepository 
from employee.services import EmployeeService
from ..attendancecalculator import AttendanceCalculator
from employee_tracking_system.utils.time_utils import TimeCalculator  
from attendance.services.realtimeupdateservice import RealTimeUpdateService
from employee.models import Employee
import logging

logger = logging.getLogger(__name__)

class CheckInOutService:
    def __init__(
        self,
        repository: AttendanceRepository,
        employee_service: EmployeeService,
        real_time_service: RealTimeUpdateService,
        attendance_calculator: AttendanceCalculator  
    ):
        self.repository = repository
        self.employee_service = employee_service
        self.real_time_service = real_time_service
        self.attendance_calculator = attendance_calculator
    
    @transaction.atomic
    def handle_check_in(self, employee: Employee) -> dict:
        now_utc = timezone.now()
        local_timezone = timezone.get_default_timezone()
        now_local = timezone.localtime(now_utc, local_timezone)
        today = now_local.date()


        if not self.attendance_calculator.is_working_time(now_local):
            return {"error": "Cannot check in outside working hours."}


        if self.repository.is_employee_on_leave(employee.id, today):
            return {"error": "Cannot check in while on leave."}
    

        open_atts = self.repository.get_employee_attendances(employee.id, today).filter(check_out__isnull=True)
        if open_atts.exists():
            open_atts.update(check_out=now_local, status='checked_out')
    

        attendance = self.repository.create_attendance({
            "employee": employee,
            "date": today,
            "check_in": now_local,
            "status": "checked_in"
        })
    

        self.real_time_service.update_all_real_time_attendance(employee, now_local)
    

        cache_key = f"attendance:{employee.id}:{today}"
        cache_data = {"check_in": now_local.isoformat(), "check_out": None}
        cache.set(cache_key, cache_data, timeout=86400)
    

        return self.get_attendance_status(employee)
    
    @transaction.atomic
    def handle_check_out(self, employee: Employee) -> dict:
        now_utc = timezone.now()
        local_timezone = timezone.get_default_timezone()
        now_local = timezone.localtime(now_utc, local_timezone)
        today = now_local.date()

        if not self.attendance_calculator.is_working_time(now_local):
            return {"error": "Cannot check out outside working hours."}

        if self.repository.is_employee_on_leave(employee.id, today):
            return {"error": "Cannot check out while on leave."}
    
        latest_att = (
            self.repository.get_employee_attendances(employee.id, today)
                        .filter(check_out__isnull=True)
                        .last()
        )
        if not latest_att:
            return {"error": "You need to check in first."}

        latest_att.check_out = now_local
        latest_att.status = 'checked_out'
        latest_att.save()
    

        self.real_time_service.update_all_real_time_attendance(employee, now_local)
    
        cache_key = f"attendance:{employee.id}:{today}"
        cache_data = cache.get(cache_key) or {}
        cache_data["check_out"] = now_local.isoformat()
        cache.set(cache_key, cache_data, timeout=86400)
    

        return self.get_attendance_status(employee)
    
    def get_attendance_status(self, employee: Employee, include_no_check_in: bool = True) -> dict:
        now_local = timezone.localtime(timezone.now())
        today = now_local.date()

        attendances_today = self.repository.get_employee_attendances(employee.id, today)


        reg_dt = getattr(employee, 'registration_datetime', None)  

        daily_lateness = self.attendance_calculator.calculate_lateness(
            attendances=attendances_today,
            now=now_local,
            include_no_check_in=include_no_check_in,
            registration_dt=reg_dt 
        )
        daily_work = self.attendance_calculator.calculate_work_duration(
            attendances=attendances_today,
            now=now_local
        )
        AttendanceModel = apps.get_model("attendance", "Attendance")
        status = AttendanceModel.objects.determine_attendance_status(attendances_today, now_local, today)
    
    
        check_in_times = [TimeCalculator.format_datetime(a.check_in) for a in attendances_today if a.check_in]
        check_out_times = [TimeCalculator.format_datetime(a.check_out) for a in attendances_today if a.check_out]
    
        return {
            "date": str(today),
            "check_ins": check_in_times if check_in_times else ["N/A"],
            "check_outs": check_out_times if check_out_times else ["N/A"],
            "lateness": TimeCalculator.timedelta_to_hhmm(daily_lateness),
            "work_duration": TimeCalculator.timedelta_to_hhmm(daily_work),
            "status": status
        }