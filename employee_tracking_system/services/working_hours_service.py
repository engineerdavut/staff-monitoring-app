import logging
from employee_tracking_system.models.working_hours import WorkingHours
from django.utils import timezone
from datetime import datetime

logger = logging.getLogger(__name__)
class WorkingHoursService:
    @staticmethod
    def get_working_hours():
        working_hours = WorkingHours.get_current()
        if not working_hours:
            logger.error("No current WorkingHours configuration found.")
            raise ValueError("Working hours configuration is missing.")
        return {
            'start_time': working_hours.start_time, 
            'end_time': working_hours.end_time
        }
    
    @staticmethod
    def is_working_hours(current_time: datetime) -> bool:
        try:
            working_hours = WorkingHoursService.get_working_hours()
            start_work_dt = timezone.make_aware(datetime.combine(current_time.date(), working_hours['start_time']))
            end_work_dt = timezone.make_aware(datetime.combine(current_time.date(), working_hours['end_time']))
            return start_work_dt <= current_time <= end_work_dt
        except Exception as e:
            logger.error(f"Error in is_working_hours: {e}")
            return False