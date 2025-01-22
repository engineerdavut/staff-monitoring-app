from datetime import datetime, date, timedelta
from typing import List, Union
from django.utils import timezone  
import logging

logger = logging.getLogger(__name__)

class TimeCalculator:
    @staticmethod
    def is_working_day(day: Union[datetime, date], holidays: List[Union[datetime, date]] = None) -> bool:
        if holidays is None:
            holidays = []
        if isinstance(day, datetime):
            day = day.date()
        return day.weekday() < 5 and day not in holidays

    @staticmethod
    def count_working_days(start_date: Union[datetime, date], end_date: Union[datetime, date], holidays: List[Union[datetime, date]] = None) -> int:
        if holidays is None:
            holidays = []

        if isinstance(start_date, datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime):
            end_date = end_date.date()

        working_days = 0
        current_date = start_date
        while current_date <= end_date:
            if TimeCalculator.is_working_day(current_date, holidays):
                working_days += 1
            current_date += timedelta(days=1)
        return working_days

    @staticmethod
    def split_leave_across_years(start_date: date, end_date: date, holidays: List[date] = None) -> dict:
        if holidays is None:
            holidays = []

        years = {}
        current_date = start_date
        while current_date <= end_date:
            year = current_date.year
            if year not in years:
                years[year] = 0
            if TimeCalculator.is_working_day(current_date, holidays):
                years[year] += 1
            current_date += timedelta(days=1)
        return years

    @staticmethod
    def timedelta_to_hhmm(td: timedelta) -> str:
        total_minutes = int(td.total_seconds() / 60)
        hours, minutes = divmod(total_minutes, 60)
        return f"{hours:02d}:{minutes:02d}"

    @staticmethod
    def format_datetime(dt):
        if dt:
            return dt.strftime('%Y-%m-%d %H:%M')
        return "N/A"

    @staticmethod
    def parse_timedelta(time_str: str) -> timedelta:
        try:
            days, hours, minutes = 0, 0, 0
            parts = time_str.split()
            for part in parts:
                if 'd' in part:
                    days = int(part.replace('d', ''))
                elif 'h' in part:
                    hours = int(part.replace('h', ''))
                elif 'm' in part:
                    minutes = int(part.replace('m', ''))
            return timedelta(days=days, hours=hours, minutes=minutes)
        except Exception as e:
            logger.error(f"Error parsing timedelta from '{time_str}': {e}")
            return timedelta()

    @staticmethod
    def get_working_days_in_month(year: int, month: int) -> List[date]:
        """
        Returns a list of working days in the specified month up to the current day if the month is the current month.
        If the specified month is in the past, returns all working days of that month.
        If the specified month is in the future, returns an empty list.
        """
        today = timezone.localtime(timezone.now()).date()

        # Belirtilen yıl ve ay gelecekte ise boş liste döndür
        if (year, month) > (today.year, today.month):
            return []

        first_day = date(year, month, 1)

        if (year, month) == (today.year, today.month):
            up_to_day = today.day
        else:
            # Geçmiş aylarda tüm günleri hesaba kat
            if month == 12:
                up_to_day = 31
            else:
                up_to_day = (date(year, month + 1, 1) - timedelta(days=1)).day

        working_days = []
        for day in range(1, up_to_day + 1):
            current_day = date(year, month, day)
            if TimeCalculator.is_working_day(current_day):
                working_days.append(current_day)

        return working_days
