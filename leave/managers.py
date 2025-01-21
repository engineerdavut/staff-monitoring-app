from django.db import models
from employee_tracking_system.utils.time_utils import TimeCalculator


class LeaveManager(models.Manager):
    def calculate_leave_days(self, start_date, end_date, holidays=None):
        return TimeCalculator.count_working_days(start_date, end_date, holidays)