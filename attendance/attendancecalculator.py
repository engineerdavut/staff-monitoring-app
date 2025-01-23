from datetime import datetime, timedelta
from django.utils import timezone
from employee_tracking_system.utils.time_utils import TimeCalculator
from employee_tracking_system.services.working_hours_service import WorkingHoursService
from .models import Attendance  
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class AttendanceCalculator:
    @staticmethod
    def calculate_lateness(
        attendances: List['Attendance'],
        now: Optional[datetime] = None,
        include_no_check_in: bool = False
    ) -> timedelta:
        working_hours = WorkingHoursService.get_working_hours()

        if now is None:
            now = timezone.localtime(timezone.now())
        today = now.date()

        start_of_work = timezone.localtime(timezone.make_aware(datetime.combine(today, working_hours['start_time'])))
        end_of_work = timezone.localtime(timezone.make_aware(datetime.combine(today, working_hours['end_time'])))

        if now > end_of_work:
            scheduled_end = end_of_work
        else:
            scheduled_end = now

        scheduled_work_duration = scheduled_end - start_of_work

        lateness = timedelta()

        if any(att.status == 'on_leave' for att in attendances):
            return lateness

        if not attendances:
            if include_no_check_in and TimeCalculator.is_working_day(today):
                if now > start_of_work:
                    lateness += scheduled_end - start_of_work
            return lateness

        total_presence = AttendanceCalculator.get_total_presence_time(attendances, start_of_work, scheduled_end)

        lateness = scheduled_work_duration - total_presence

        if lateness < timedelta():
            lateness = timedelta()

        return lateness

    @staticmethod
    def calculate_work_duration(
        attendances: List['Attendance'],
        now: Optional[datetime] = None
    ) -> timedelta:
        working_hours = WorkingHoursService.get_working_hours()

        if now is None:
            now = timezone.localtime(timezone.now())
        today = now.date()

        start_of_work = timezone.localtime(timezone.make_aware(datetime.combine(today, working_hours['start_time'])))
        end_of_work = timezone.localtime(timezone.make_aware(datetime.combine(today, working_hours['end_time'])))

        if now > end_of_work:
            scheduled_end = end_of_work
        else:
            scheduled_end = now

        work_duration = timedelta()

        if any(att.status == 'on_leave' for att in attendances):
            return work_duration

        if not attendances:
            return work_duration

        total_presence = AttendanceCalculator.get_total_presence_time(attendances, start_of_work, scheduled_end)

        work_duration = total_presence

        return work_duration

    @staticmethod
    def get_total_presence_time(attendances: List['Attendance'], scheduled_start: datetime, scheduled_end: datetime) -> timedelta:
        total_presence = timedelta()

        sorted_attendances = sorted(attendances, key=lambda x: x.check_in if x.check_in else x.check_out)

        for att in sorted_attendances:
            if att.status == 'on_leave':
                continue  

            check_in = att.check_in
            check_out = att.check_out


            if not check_in:
                continue

            actual_check_in = max(check_in, scheduled_start)
            if check_out:
                actual_check_out = min(check_out, scheduled_end)
            else:
                actual_check_out = scheduled_end

            if actual_check_in > scheduled_end:
                continue

            if check_out and check_out < scheduled_start:
                continue

            if actual_check_out > actual_check_in:
                presence = actual_check_out - actual_check_in
                total_presence += presence

        return total_presence

    @staticmethod
    def is_working_time(current_time: datetime) -> bool:
        return (
            TimeCalculator.is_working_day(current_time.date())
            and WorkingHoursService.is_working_hours(current_time)
        )
