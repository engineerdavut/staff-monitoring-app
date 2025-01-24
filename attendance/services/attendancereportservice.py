from datetime import datetime, timedelta, date
from typing import Dict, Any, List
from django.utils import timezone
from employee_tracking_system.utils.time_utils import TimeCalculator
from django.core.cache import cache
from django.conf import settings
from redis import Redis
from redis.lock import Lock
from ..serializers import AttendanceReportSerializer  
from collections import defaultdict  
from employee_tracking_system.services.working_hours_service import WorkingHoursService
import logging

logger = logging.getLogger(__name__)

class AttendanceReportService:
    def __init__(self, repository, attendance_calculator, employee_service):
        self.repository = repository
        self.attendance_calculator = attendance_calculator
        self.employee_service = employee_service

    def get_week_start_end_date(self, year: int, month: int, week: int):
        first_day_of_month = date(year, month, 1)
        first_monday = first_day_of_month + timedelta(days=(0 - first_day_of_month.weekday() + 7) % 7)
        start_date = first_monday + timedelta(weeks=week - 1)
        end_date = start_date + timedelta(days=6)
        return start_date, end_date

    def get_weekly_report(self, year: int, month: int, week: int) -> List[Dict[str, Any]]:
        start_date, end_date = self.get_week_start_end_date(year, month, week)
        cache_key = f'weekly_report_{year}_{month}_{week}'
        cached_report = cache.get(cache_key)
        if cached_report:
            logger.info(f"Fetching weekly report from cache {cache_key}")
            return cached_report

        all_attendances = self.repository.get_all_attendances_between_dates(start_date, end_date)
        employees = self.employee_service.get_all_employees()  
        weekly_report = []

        for employee in employees:
            try:
                employee_attendances = [a for a in all_attendances if a.employee == employee]
                total_work_time = timedelta()
                total_lateness = timedelta()
                days_worked = set()
                days_late = set()
                for attendance in employee_attendances:
                    if attendance.status in ['on_leave', 'not_working_day', 'not_working_hour']:
                        continue  # Bu durumlarda lateness hesaplanmaz
                    daily_work_time = self.attendance_calculator.calculate_work_duration(
                        attendances=[attendance], 
                        now=timezone.now()
                    )
                    daily_lateness = self.attendance_calculator.calculate_lateness(
                        attendances=[attendance],
                        now=timezone.now(),
                        include_no_check_in=False
                    )
                    total_work_time += daily_work_time
                    total_lateness += daily_lateness
                    days_worked.add(attendance.date)
                    if daily_lateness > timedelta():
                        days_late.add(attendance.date)
                days_worked_count = len(days_worked)
                days_late_count = len(days_late)
                avg_daily_hours = total_work_time / days_worked_count if days_worked_count > 0 else timedelta()

                weekly_report.append({
                    'employee': employee.user.username,
                    'total_hours': TimeCalculator.timedelta_to_hhmm(total_work_time),
                    'total_lateness': TimeCalculator.timedelta_to_hhmm(total_lateness),
                    'avg_daily_hours': TimeCalculator.timedelta_to_hhmm(avg_daily_hours),
                    'days_worked': days_worked_count,
                    'days_late': days_late_count,
                })
            except Exception as e:
                logger.error(f"Error processing weekly report for employee {employee.id}: {e}")
                weekly_report.append({
                    'employee': employee.user.username,
                    'total_hours': "N/A",
                    'total_lateness': "N/A",
                    'avg_daily_hours': "N/A",
                    'days_worked': "N/A",
                    'days_late': "N/A",
                })

        cache.set(cache_key, weekly_report, settings.WEEKLY_REPORT_CACHE_TIMEOUT)
        logger.info(f"Weekly report cached with key {cache_key}")
        return weekly_report

    def get_monthly_report(self, year: int, month: int) -> List[Dict[str, Any]]:
        start_date = date(year, month, 1)
        now_local = timezone.localtime(timezone.now())
        today = now_local.date()

        if (year, month) > (today.year, today.month):
            working_days = []
        else:
            working_days = TimeCalculator.get_working_days_in_month(year, month)

        cache_key = f"monthly_report_{year}_{month}"
        cached_report = cache.get(cache_key)
        if cached_report:
            logger.info(f"Fetching monthly report from cache {cache_key}")
            return cached_report

        if working_days:
            if today in working_days:
                end_date = today
            else:
                end_date = working_days[-1]
        else:
            end_date = start_date  

        all_attendances = self.repository.get_all_attendances_between_dates(start_date, end_date)
        employees = self.employee_service.get_all_employees()
        monthly_report = []

        for employee in employees:
            try:

                reg_dt = getattr(employee, 'registration_datetime', None)
                employee_attendances = [
                    att for att in all_attendances if att.employee_id == employee.id
                ]
                attendances_by_date = defaultdict(list)
                for attendance in employee_attendances:
                    attendances_by_date[attendance.date].append(attendance)

                total_work_time = timedelta(0)
                total_lateness = timedelta(0)
                days_worked = set()
                days_late = set()

                for attendance_date, attendances_list in attendances_by_date.items():

                    if reg_dt and attendance_date < reg_dt.date():
                        continue
                    if attendance_date > today:
                        continue

                    working_hours = WorkingHoursService.get_working_hours()
                    if attendance_date == today:
                        current_now = now_local
                    else:
                        current_now = timezone.localtime(
                            timezone.make_aware(datetime.combine(
                                attendance_date, working_hours['end_time']
                            ))
                        )

                    daily_lateness = self.attendance_calculator.calculate_lateness(
                        attendances=attendances_list,
                        now=current_now,
                        include_no_check_in=True,
                        registration_dt=reg_dt  
                    )
                    daily_work_time = self.attendance_calculator.calculate_work_duration(
                        attendances=attendances_list,
                        now=current_now
                    )

                    total_lateness += daily_lateness
                    total_work_time += daily_work_time
                    days_worked.add(attendance_date)

                    if daily_lateness > timedelta(0):
                        days_late.add(attendance_date)

                for wd in working_days:
                    if reg_dt and wd < reg_dt.date():
                        continue
                    if wd > today:
                        continue
                    if wd in days_worked:
                        continue

                    working_hours = WorkingHoursService.get_working_hours()
                    if wd == today:
                        current_now = now_local
                    else:
                        current_now = timezone.localtime(
                            timezone.make_aware(datetime.combine(wd, working_hours['end_time']))
                        )
                    lateness = self.attendance_calculator.calculate_lateness(
                        attendances=[],
                        now=current_now,
                        include_no_check_in=True,
                        registration_dt=reg_dt 
                    )
                    total_lateness += lateness
                    if lateness > timedelta(0):
                        days_late.add(wd)

                days_worked_count = len(days_worked)
                days_late_count = len(days_late)
                if days_worked_count > 0:
                    avg_daily_hours = total_work_time / days_worked_count
                else:
                    avg_daily_hours = timedelta(0)

                monthly_report.append({
                    'employee': employee.user.username,
                    'total_hours': TimeCalculator.timedelta_to_hhmm(total_work_time),
                    'total_lateness': TimeCalculator.timedelta_to_hhmm(total_lateness),
                    'avg_daily_hours': TimeCalculator.timedelta_to_hhmm(avg_daily_hours),
                    'days_worked': days_worked_count,
                    'days_late': days_late_count,
                })

            except Exception as e:
                logger.error(f"Error processing monthly report for employee {employee.id}: {e}")
                monthly_report.append({
                    'employee': employee.user.username,
                    'total_hours': "N/A",
                    'total_lateness': "N/A",
                    'avg_daily_hours': "N/A",
                    'days_worked': "N/A",
                    'days_late': "N/A",
                })

        cache.set(cache_key, monthly_report, settings.MONTHLY_REPORT_CACHE_TIMEOUT)
        logger.info(f"Monthly report cached with key {cache_key}")
        return monthly_report

    def get_monthly_report_serialized(self, year: int, month: int) -> List[Dict[str, Any]]:
        report_data = self.get_monthly_report(year, month)
        serializer = AttendanceReportSerializer(report_data, many=True)
        return serializer.data