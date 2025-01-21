# employee/iemployeerepository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date, timedelta
from .models import Employee

class IEmployeeRepository(ABC):
    @abstractmethod
    def get_employee(self, employee_id: int) -> Optional[Employee]:
        pass

    
    @abstractmethod
    def get_all_employees(self) -> List[Employee]:
        pass

    @abstractmethod
    def get_employees_without_checkin(self, target_date: date) -> List[Employee]:
        pass

    @abstractmethod
    def get_authorized_employees(self) -> List[Employee]:
        pass

    @abstractmethod
    def get_employees_with_low_leave_balance(self, threshold: int) -> List[Employee]:
        pass

    @abstractmethod
    def update_employee_leave(self, employee: Employee, lateness: str) -> None:
        pass
    
    @abstractmethod
    def update_employee_total_lateness(self,employee: Employee, lateness: timedelta, work_duration: timedelta) -> None:
        pass