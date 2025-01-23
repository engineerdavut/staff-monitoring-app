from celery import shared_task
from django.utils import timezone
from employee_tracking_system.utils.notification_utils import send_notification
from .utils import get_employee_service
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)

from attendance.utils import (
    get_check_in_out_service, 
    get_realtime_update_service, 
    get_attendance_report_service, 
    get_attendance_calculator,
    get_employee_service
)

@shared_task
def reset_annual_leave():
    employee_service = get_employee_service()
    employees = employee_service.get_all_employees()
    for employee in employees:
        employee_service.reset_annual_leave(employee)
    logger.info("Annual leave reset completed for all employees")
    return "Annual leave reset completed for all employees"

@shared_task
def check_low_leave_balance(threshold=3):
    try:
        employee_service = get_employee_service()
        employees = employee_service.get_employees_with_low_leave_balance(threshold_days=threshold)

        for employee in employees:
            send_notification(
                user=employee.user,
                notification_type="LOW_LEAVE_BALANCE",
                employee=employee.user.username,
                balance=employee_service.get_remaining_leave_display(employee)
            )
            authorized_users = employee_service.get_authorized_employees()
            for auth_user in authorized_users:
                send_notification(
                    user=auth_user.user,
                    notification_type="LOW_LEAVE_BALANCE",
                    employee=employee.user.username,
                    balance=employee_service.get_remaining_leave_display(employee)
                )
        
        logger.info(f"check_low_leave_balance: Found {len(employees)} employees below threshold={threshold}.")
        return f"check_low_leave_balance: Found {len(employees)} employees below threshold={threshold}."
    except Exception as e:
        logger.error(f"Error in check_low_leave_balance task: {e}")
        return f"Error in check_low_leave_balance task: {e}"

@shared_task
def notify_no_check_in_for_today():
    today = timezone.now().date()
    employee_service = get_employee_service()
    employees_without_checkin = employee_service.get_employees_without_check_in(today)
    for employee in employees_without_checkin:
        send_notification(
            user=employee.user,
            notification_type="NO_CHECK_IN",
            employee=employee.user.username,
        )
        authorized_users = employee_service.get_authorized_employees()
        for auth_user in authorized_users:
            send_notification(
                user=auth_user.user,
                notification_type="NO_CHECK_IN",
                employee=employee.user.username,
            )
    logger.info("notify_no_check_in_for_today: Notifications sent.")
    return "notify_no_check_in_for_today: Notifications sent."


@shared_task
def update_remaining_leave(employee_id, new_remaining_leave):
    channel_layer = get_channel_layer()
    group_name = f"employee_{employee_id}"

    message = {
        'type': 'remaining_leave_update',
        'remaining_leave': new_remaining_leave,
    }

    async_to_sync(channel_layer.group_send)(
        group_name,
        message
    )
    logger.info(f"update_remaining_leave: Sent remaining_leave update to employee {employee_id}.")
    return f"update_remaining_leave: Sent remaining_leave update to employee {employee_id}."
@shared_task
def update_employee_totals():
    try:
        employee_service = get_employee_service()
        employees = employee_service.get_all_employees()
        today = timezone.now().date()
        for emp in employees:
            attendances = emp.attendances.filter(date=today)
            daily_lateness = get_attendance_calculator().calculate_lateness(
                attendances=attendances,
                now=timezone.localtime(timezone.now()),
                include_no_check_in=False
            )
            daily_work_duration = get_attendance_calculator().calculate_work_duration(
                attendances=attendances,
                now=timezone.localtime(timezone.now())
            )
            employee_service.increment_total_work_duration(emp, daily_work_duration)
            employee_service.increment_total_lateness(emp, daily_lateness)
            employee_service.update_remaining_leave(emp,daily_lateness)


        logger.info("update_employee_totals: Total lateness and work duration updated for all employees.")
    except Exception as e:
        logger.error(f"Error in update_employee_totals task: {e}")