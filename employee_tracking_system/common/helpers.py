from attendance.attendancecalculator import AttendanceCalculator
from ..services.working_hours_service import WorkingHoursService

def get_attendance_calculator():
    return AttendanceCalculator()

def get_working_hours_service():
    return WorkingHoursService()