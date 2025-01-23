from .employeerepository import EmployeeRepository
from attendance.attendancerepository import AttendanceRepository
from attendance.iattendancerepository import IAttendanceRepository
from .iemployeerepository import IEmployeeRepository



def get_employee_repository() -> IEmployeeRepository:
    return EmployeeRepository()

def get_attendance_repository() -> IAttendanceRepository:
    return AttendanceRepository()

def get_employee_service():
    from attendance.utils import get_employee_service  
    return get_employee_service()

def get_check_in_out_service():
    from attendance.utils import get_check_in_out_service 
    return get_check_in_out_service()

def get_realtime_update_service():
    from attendance.utils import get_realtime_update_service  
    return get_realtime_update_service()

def get_attendance_report_service():
    from attendance.utils import get_attendance_report_service  
    return get_attendance_report_service()
def get_attendance_calculator(): 
    from attendance.attendancecalculator import AttendanceCalculator 
    return AttendanceCalculator()

def get_working_hours_service(): 
    from employee_tracking_system.common.helpers import get_working_hours_service
    return get_working_hours_service()