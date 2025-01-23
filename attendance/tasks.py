from celery import shared_task
from django.utils import timezone
from employee_tracking_system.utils.notification_utils import send_notification 
from typing import List, Dict, Any  
from django.dispatch import receiver  
from django.db.models.signals import post_save  
from .models import Attendance
import logging

logger = logging.getLogger(__name__)

from .utils import (
    get_realtime_update_service, 
    get_attendance_report_service, 
    get_employee_service,
    get_attendance_calculator,
    get_working_hours_service,
    get_check_in_out_service
)

@shared_task
def daily_work_summary():
    try:
        today = timezone.now().date()
        check_in_out_service = get_check_in_out_service()

        attendances = check_in_out_service.repository.get_checked_out_attendances(today)
        for attendance in attendances:
            work_hours = (attendance.check_out - attendance.check_in).total_seconds() / 3600
            send_notification(
                user=attendance.employee.user,
                notification_type="DAILY_WORK_SUMMARY",
                hours=round(work_hours, 2),
                send_realtime=True
            )
        logger.info("daily_work_summary: Sent daily work summary notifications.")
    except Exception as e:
        logger.error(f"Error in daily_work_summary task: {e}")

@shared_task
def check_employee_lateness():
    try:
        employee_service = get_employee_service()
        employees = employee_service.get_all_employees()
        for employee in employees:
            employee_service.calculate_daily_lateness(employee)
        logger.info("check_employee_lateness: Processed late attendances.")
    except Exception as e:
        logger.error(f"Error in check_employee_lateness task: {e}")

@shared_task(
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 5, 'countdown': 10},
    retry_backoff=True,
)
def update_real_time_attendance():
    try:
        realtime_update_service = get_realtime_update_service()
        realtime_update_service.update_all_real_time_attendance()
        logger.info("update_real_time_attendance: Task executed successfully")
    except Exception as e:
        logger.error(f"Error in update_real_time_attendance task: {e}")
        raise

@shared_task
def generate_monthly_report_task(year: int, month: int) -> List[Dict[str, Any]]:
    try:
        report_service = get_attendance_report_service()
        report = report_service.get_monthly_report(year, month)
        return report
    except Exception as e:
        logger.error(f"Error in generate_monthly_report_task: {e}")
        return []

@shared_task
def generate_weekly_report_task(year: int, month: int, week: int) -> List[Dict[str, Any]]:
    try:
        report_service = get_attendance_report_service()
        report = report_service.get_weekly_report(year, month, week)
        return report
    except Exception as e:
        logger.error(f"Error in generate_weekly_report_task: {e}")
        return []

@shared_task
def send_check_in_notification(user_id, check_in_time_str):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found.")
        return
    
    send_notification(
        user=user,
        notification_type="CHECK_IN",
        time=check_in_time_str,
        type='temporary',
        severity='success',
    )
    
    logger.info(f"send_check_in_notification: Notified user {user.username}.")
    return f"send_check_in_notification: Notified user {user.username}."

@receiver(post_save, sender=Attendance)
def check_in_post_save(sender, instance, created, **kwargs):
    if created and instance.status == 'checked_in':
        send_check_in_notification.delay(instance.employee.user.id, instance.check_in.isoformat())