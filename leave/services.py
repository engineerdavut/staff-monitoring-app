from django.db import transaction
from django.core.exceptions import ValidationError
from .leaverepository import LeaveRepository
from employee.employeerepository import EmployeeRepository
from .ileaverepository import ILeaveRepository
from employee.iemployeerepository import IEmployeeRepository
from .models import Leave
from django.utils import timezone
from datetime import timedelta
from attendance.services import AttendanceService
import logging

logger = logging.getLogger(__name__)

class LeaveService:
    def __init__(self, leave_repository: ILeaveRepository = None, employee_repository: IEmployeeRepository = None, attendance_service: AttendanceService = None):
        self.leave_repository = leave_repository or LeaveRepository()
        self.employee_repository = employee_repository or EmployeeRepository()
        self.attendance_service = attendance_service or AttendanceService()  

    @transaction.atomic
    def request_leave(self, employee, start_date, end_date, reason, holidays=None):
        if not employee:
            raise ValidationError("Employee not found.")

        self._validate_leave_request(employee, start_date, end_date, holidays)

        leave_days = self.leave_repository.calculate_leave_days(start_date, end_date, holidays)
        remaining_leave = self.leave_repository.get_remaining_leave(employee)
        logger.debug(f"Requesting leave: leave_days={leave_days}, remaining_leave={remaining_leave}")
        if leave_days > remaining_leave:
            raise ValidationError("Not enough leave days available.")

        leave_data = {
            "employee": employee,
            "start_date": start_date,
            "end_date": end_date,
            "reason": reason,
            "status": Leave.PENDING
        }
        leave = self.leave_repository.create_leave(leave_data)
        logger.info(f"Leave request created for employee {employee.user.username}.")
        return leave

    @transaction.atomic
    def create_approved_leave(self, employee, start_date, end_date, reason, holidays=None):
        if not employee:
            raise ValidationError("Employee not found.")


        self._validate_leave_request(employee, start_date, end_date, holidays)


        leave_days = self.leave_repository.calculate_leave_days(start_date, end_date, holidays)
        remaining_leave = self.leave_repository.get_remaining_leave(employee)
        logger.debug(f"Creating approved leave: leave_days={leave_days}, remaining_leave={remaining_leave}")


        overlapping_leaves = self.leave_repository.get_overlapping_leaves(employee, start_date, end_date)
        if overlapping_leaves.exists():
            leave_data = {
                "employee": employee,
                "start_date": start_date,
                "end_date": end_date,
                "reason": reason,
                "status": Leave.REJECTED
            }
            leave = self.leave_repository.create_leave(leave_data)
            logger.info(f"Leave request automatically rejected for employee {employee.user.username} due to overlapping leaves.")
            return leave

        if leave_days > remaining_leave:
            leave_data = {
                "employee": employee,
                "start_date": start_date,
                "end_date": end_date,
                "reason": reason,
                "status": Leave.REJECTED
            }
            leave = self.leave_repository.create_leave(leave_data)
            logger.info(f"Leave request automatically rejected for employee {employee.user.username} due to insufficient leave days.")
            return leave

        self.leave_repository.update_remaining_leave(employee, leave_days)

        leave_data = {
            "employee": employee,
            "start_date": start_date,
            "end_date": end_date,
            "reason": reason,
            "status": Leave.APPROVED
        }
        leave = self.leave_repository.create_leave(leave_data)
        logger.info(f"Approved leave created for employee {employee.user.username}.")

        try:
            self.attendance_service.set_employee_on_leave(employee, start_date, end_date)
        except ValidationError as ve:
            leave.status = Leave.REJECTED
            leave.updated_at = timezone.now()
            self.leave_repository.update_leave(leave)
            logger.error(f"Failed to set attendance on_leave for leave {leave.id}: {ve}")
            raise ValidationError(f"Leave approved but failed to update attendance: {ve}")

        return leave

    def _validate_leave_request(self, employee, start_date, end_date, holidays=None):
        if start_date > end_date:
            raise ValidationError("End date must be after start date.")

        tomorrow = timezone.now().date() + timedelta(days=1)
        if start_date < tomorrow:
            raise ValidationError("Start date cannot be before tomorrow.")

        overlapping_leaves = self.leave_repository.get_overlapping_leaves(employee, start_date, end_date)
        if overlapping_leaves.exists():
            conflicting_leaves = overlapping_leaves.values_list('start_date', 'end_date')
            conflict_dates = ", ".join([f"{start} to {end}" for start, end in conflicting_leaves])
            raise ValidationError(f"Your leave request overlaps with existing leaves: {conflict_dates}.")
    
    @transaction.atomic
    def approve_leave(self, leave_id):
        leave = self.leave_repository.get_leave(leave_id)
        if not leave:
            raise ValidationError("Leave not found.")
        if leave.status != Leave.PENDING:
            raise ValidationError("Only pending leaves can be approved.")

        today = timezone.now().date()
        if leave.start_date < today:
            leave.status = Leave.REJECTED
            leave.updated_at = timezone.now()
            self.leave_repository.update_leave(leave)
            logger.warning(f"Leave {leave_id} automatically rejected because start_date < today.")
            return {
                "status": "rejected",
                "message": "Cannot approve leave requests that have already started.",
                "leave": leave
            }

        leave_days = self.leave_repository.calculate_leave_days(leave.start_date, leave.end_date)
        employee = leave.employee
        remaining_leave = self.leave_repository.get_remaining_leave(employee)
        logger.debug(f"Approving leave: leave_days={leave_days}, remaining_leave={remaining_leave}")
        if leave_days > remaining_leave:
            leave.status = Leave.REJECTED
            leave.updated_at = timezone.now()
            self.leave_repository.update_leave(leave)
            logger.warning(f"Leave {leave_id} automatically rejected due to insufficient leave days.")
            return {
                "status": "rejected",
                "message": "Employee does not have enough remaining leave days.",
                "leave": leave
            }

        self.leave_repository.update_remaining_leave(employee, leave_days)

        leave.status = Leave.APPROVED
        leave.updated_at = timezone.now()
        self.leave_repository.update_leave(leave)
        logger.info(f"Leave {leave_id} approved.")

        try:
            self.attendance_service.set_employee_on_leave(employee, leave.start_date, leave.end_date)
        except ValidationError as ve:
            leave.status = Leave.REJECTED
            leave.updated_at = timezone.now()
            self.leave_repository.update_leave(leave)
            logger.error(f"Failed to set attendance on_leave for leave {leave.id}: {ve}")
            return {
                "status": "rejected",
                "message": f"Leave approved but failed to update attendance: {ve}",
                "leave": leave
            }

        return {
            "status": "approved",
            "message": "Leave approved successfully.",
            "leave": leave
        }

    @transaction.atomic
    def reject_leave(self, leave_id):
        leave = self.leave_repository.get_leave(leave_id)
        if not leave:
            raise ValidationError("Leave not found.")
        if leave.status != Leave.PENDING:
            raise ValidationError("Only pending leaves can be rejected.")
        leave.status = Leave.REJECTED
        leave.updated_at = timezone.now()
        self.leave_repository.update_leave(leave)
        logger.info(f"Leave {leave_id} rejected.")
        return leave

    @transaction.atomic
    def cancel_leave(self, leave_id):
        leave = self.leave_repository.get_leave(leave_id)
        if not leave:
            raise ValidationError("Leave not found.")
        if leave.status != Leave.PENDING:
            raise ValidationError("Only pending leaves can be cancelled.")

        leave.status = Leave.CANCELLED
        leave.updated_at = timezone.now()
        self.leave_repository.update_leave(leave)
        logger.info(f"Leave {leave_id} cancelled.")
        return leave

    def get_employee_leaves(self, employee):
        return self.leave_repository.get_employee_leaves(employee)

    def get_all_leaves(self):
        return self.leave_repository.get_all_leaves()