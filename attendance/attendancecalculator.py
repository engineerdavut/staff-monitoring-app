# attendance/calculator.py

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

        # now'ı, end_of_work'ı aşmaması için kısıtla
        if now > end_of_work:
            scheduled_end = end_of_work
        else:
            scheduled_end = now

        # Toplam planlanan çalışma süresi
        scheduled_work_duration = scheduled_end - start_of_work

        lateness = timedelta()

        # 1. on_leave durumunda lateness 00:00 olmalı.
        if any(att.status == 'on_leave' for att in attendances):
            return lateness

        # 2. not_checked_in durumunda hesaplama olmalı.
        if not attendances:
            if include_no_check_in and TimeCalculator.is_working_day(today):
                if now > start_of_work:
                    lateness += scheduled_end - start_of_work
            return lateness

        # 3. Çoklu check-in checkout olmalı.
        # Lateness'i toplam yokluk süresi olarak hesaplayacağız.
        total_presence = AttendanceCalculator.get_total_presence_time(attendances, start_of_work, scheduled_end)

        # Lateness = Planlanan çalışma süresi - Toplam varlık süresi
        lateness = scheduled_work_duration - total_presence

        # Lateness'in negatif olmamasını sağla
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

        # now'ı, end_of_work'ı aşmaması için kısıtla
        if now > end_of_work:
            scheduled_end = end_of_work
        else:
            scheduled_end = now

        # Initialize work_duration
        work_duration = timedelta()

        # 1. on_leave durumunda work_duration 00:00 olmalı.
        if any(att.status == 'on_leave' for att in attendances):
            return work_duration

        # 2. not_checked_in durumunda work_duration sabit kalır.
        if not attendances:
            return work_duration

        # 3. Çoklu check-in checkout olmalı.
        # Toplam varlık süresini hesapla
        total_presence = AttendanceCalculator.get_total_presence_time(attendances, start_of_work, scheduled_end)

        # work_duration = total_presence
        work_duration = total_presence

        return work_duration

    @staticmethod
    def get_total_presence_time(attendances: List['Attendance'], scheduled_start: datetime, scheduled_end: datetime) -> timedelta:
        """
        Çalışma saatleri içinde çalışan süresini hesaplar, çoklu check-in/check-out işlemlerini doğru şekilde ele alır.
        """
        total_presence = timedelta()

        # Attendances listesini check_in zamanına göre sırala
        sorted_attendances = sorted(attendances, key=lambda x: x.check_in if x.check_in else x.check_out)

        for att in sorted_attendances:
            if att.status == 'on_leave':
                continue  # zaten handled

            check_in = att.check_in
            check_out = att.check_out

            # Eğer hiç check_in yoksa, yokluk süresi olarak kabul edilir
            if not check_in:
                continue

            # Gerçek check_in ve check_out zamanlarını belirle
            actual_check_in = max(check_in, scheduled_start)
            if check_out:
                actual_check_out = min(check_out, scheduled_end)
            else:
                actual_check_out = scheduled_end

            # Eğer check_in > scheduled_end, yokluk süresi eklenmez
            if actual_check_in > scheduled_end:
                continue

            # Eğer check_out < scheduled_start, yokluk süresi eklenmez
            if check_out and check_out < scheduled_start:
                continue

            # Varlık süresi hesapla
            if actual_check_out > actual_check_in:
                presence = actual_check_out - actual_check_in
                total_presence += presence

        return total_presence

    @staticmethod
    def is_working_time(current_time: datetime) -> bool:
        """
        Çalışma günü ve çalışma saatinde olup olmadığını kontrol eder.
        """
        return (
            TimeCalculator.is_working_day(current_time.date())
            and WorkingHoursService.is_working_hours(current_time)
        )

    @staticmethod
    def is_working_time(current_time: datetime) -> bool:
        """
        Çalışma günü ve çalışma saatinde olup olmadığını kontrol eder.
        """
        return (
            TimeCalculator.is_working_day(current_time.date())
            and WorkingHoursService.is_working_hours(current_time)
        )
