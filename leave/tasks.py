from celery import shared_task
from .services import LeaveService
from employee_tracking_system.utils.notification_utils import send_notification 
from .leaverepository import  LeaveRepository
from employee.employeerepository import EmployeeRepository
from .ileaverepository import ILeaveRepository
from employee.iemployeerepository import IEmployeeRepository 
import logging

logger = logging.getLogger(__name__)

@shared_task
def approve_leave_task(leave_id):
    leave_service = LeaveService(
        leave_repository=LeaveRepository(),
        employee_repository=EmployeeRepository()
    )
    try:
        leave = leave_service.approve_leave(leave_id)
        employee = leave.employee
        send_notification(
            user=employee.user,
            notification_type="LEAVE_APPROVED",
            leave_id=leave_id,
            start_date=leave.start_date,
            end_date=leave.end_date,
            send_realtime=True
        )
        logger.info(f"approve_leave_task: Leave {leave_id} approved.")
    except Exception as e:
        logger.error(f"approve_leave_task: Failed to approve leave {leave_id}: {str(e)}")

@shared_task
def reject_leave_task(leave_id):
    leave_service = LeaveService(
        leave_repository=LeaveRepository(),
        employee_repository=EmployeeRepository()
    )
    try:
        leave = leave_service.reject_leave(leave_id)
        employee = leave.employee
        send_notification(
            user=employee.user,
            notification_type="LEAVE_REJECTED",
            leave_id=leave_id,
            start_date=leave.start_date,
            end_date=leave.end_date,
            send_realtime=True
        )
        logger.info(f"reject_leave_task: Leave {leave_id} rejected.")
    except Exception as e:
        logger.error(f"reject_leave_task: Failed to reject leave {leave_id}: {str(e)}")

@shared_task
def cancel_leave_task(leave_id):
    leave_service = LeaveService(
        leave_repository=LeaveRepository(),
        employee_repository=EmployeeRepository()
    )
    try:
        leave = leave_service.cancel_leave(leave_id)
        employee = leave.employee
        send_notification(
            user=employee.user,
            notification_type="LEAVE_CANCELLED",
            leave_id=leave_id,
            start_date=leave.start_date,
            end_date=leave.end_date,
            send_realtime=True
        )
        logger.info(f"cancel_leave_task: Leave {leave_id} cancelled.")
    except Exception as e:
        logger.error(f"cancel_leave_task: Failed to cancel leave {leave_id}: {str(e)}")