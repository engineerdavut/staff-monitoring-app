from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING
from datetime import date, timedelta
from employee.models import Employee
from django.db.models import QuerySet

if TYPE_CHECKING:
    from .models import Attendance  

class IAttendanceRepository(ABC):
    
    @abstractmethod
    def get_employee_attendances(self, employee_id: int, date: date) -> QuerySet['Attendance']:
        pass

    @abstractmethod
    def get_all_attendances_between_dates(self, start_date: date, end_date: date) -> List['Attendance']:
        pass

    @abstractmethod
    def create_attendance(self, data: dict) -> 'Attendance':
        pass

    @abstractmethod
    def get_checked_out_attendances(self, date: date) -> List['Attendance']:
        pass

    @abstractmethod
    def get_late_attendances(self, date: date) -> List['Attendance']:
        pass

    @abstractmethod
    def calculate_employee_lateness(self, employee: Employee, date: date) -> timedelta:
        pass

    @abstractmethod
    def is_employee_on_leave(self, employee_id: int, date: date) -> bool:
        pass

    @abstractmethod
    def get_authorized_employees(self) -> List[Employee]:
        pass