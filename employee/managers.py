from django.db import models
from django.utils import timezone
from datetime import timedelta 

class EmployeeManager(models.Manager):
    def get_employees_with_low_leave(self, threshold_days=3):
        threshold = timedelta(days=threshold_days)
        return self.filter(remaining_leave__lte=threshold)

    def get_employees_without_attendance(self, date=None):
        if date is None:
            date = timezone.now().date()
        return self.filter(attendances__isnull=True, attendances__date=date)