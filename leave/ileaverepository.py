from abc import ABC, abstractmethod
from datetime import date
from typing import List
from employee.models import Employee 

class ILeaveRepository(ABC):

    @abstractmethod
    def get_leave(self, leave_id):
        pass

    @abstractmethod
    def get_employee_leaves(self, employee):
        pass
    @abstractmethod
    def get_all_leaves(self):
        pass
    @abstractmethod
    def create_leave(self, leave_data):
        pass

    @abstractmethod
    def update_leave(self, leave):
        """Updates an existing leave instance."""
        pass

    @abstractmethod
    def get_overlapping_leaves(self, employee, start_date, end_date):
        pass
    
    @abstractmethod
    def calculate_leave_days(self, start_date: date, end_date: date, holidays: List[date] = None) -> int:
        pass

    @abstractmethod
    def get_remaining_leave(self, employee: Employee) -> int:
        pass

    @abstractmethod
    def update_remaining_leave(self, employee: Employee, leave_days: int) -> int:
        pass