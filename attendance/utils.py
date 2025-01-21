from .services.checkinoutservice import CheckInOutService
from .services.realtimeupdateservice import RealTimeUpdateService
from .attendancerepository import AttendanceRepository
from employee.employeerepository import EmployeeRepository
from employee.services import EmployeeService
from employee_tracking_system.common.helpers import get_attendance_calculator, get_working_hours_service


def get_attendance_repository():
    return AttendanceRepository()

def get_employee_repository():
    return EmployeeRepository()

def get_attendance_report_service():
    from .services.attendancereportservice import AttendanceReportService
    attendance_repository = get_attendance_repository()
    attendance_calculator = get_attendance_calculator()
    employee_service = get_employee_service()
    return AttendanceReportService(attendance_repository, attendance_calculator, employee_service)

def get_employee_service():
    attendance_repository = get_attendance_repository()
    employee_repository = get_employee_repository()
    return EmployeeService(employee_repository, attendance_repository)

def get_realtime_update_service():
    attendance_repository = get_attendance_repository()
    employee_service = get_employee_service()
    return RealTimeUpdateService(attendance_repository, employee_service)

def get_check_in_out_service() -> CheckInOutService:
    repository = get_attendance_repository()
    employee_service = get_employee_service()
    real_time_service = get_realtime_update_service()
    attendance_calculator = get_attendance_calculator()
    return CheckInOutService(repository, employee_service, real_time_service, attendance_calculator)
