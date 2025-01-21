from __future__ import annotations  
from django.db import models
from employee.models import Employee
from django.utils import timezone
from django.core.exceptions import ValidationError 
from datetime import datetime, date
from employee_tracking_system.utils.time_utils import TimeCalculator  
from employee_tracking_system.services.working_hours_service import WorkingHoursService  
from django.db.models import QuerySet

class AttendanceManager(models.Manager):
   def determine_attendance_status(self, attendances: QuerySet['Attendance'], now: datetime, today: date) -> str:
        if not TimeCalculator.is_working_day(today):
            return 'not_working_day'
        elif not WorkingHoursService.is_working_hours(now):
            return 'not_working_hour'
        elif attendances.filter(status='on_leave').exists():
            return 'on_leave'
        elif not attendances.exists():
            return 'not_checked_in'
        else:
            # Attendances'ı check_out veya check_in'e göre sırala (önce check_out, sonra check_in)
            last_attendance = attendances.order_by('-check_out', '-check_in').first()
            if last_attendance and last_attendance.check_out is None:
                return 'checked_in'
            elif last_attendance:
                 return 'checked_out'
            else:
                return 'not_checked_in'

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('not_working_day', 'Not Working Day'),
        ('not_working_hour', 'Not Working Hour'),
        ('not_checked_in', 'Not Checked In'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('on_leave', 'On Leave'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField(default=timezone.now)
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    lateness = models.IntegerField(default=0) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_checked_in')  
        
    objects = AttendanceManager()  

    def clean(self):
        if self.check_out and self.check_in and self.check_out <= self.check_in:
            raise ValidationError("Check-out time must be after check-in time.")

    def save(self, *args, **kwargs):
        # Status belirleme
        if self.status != 'on_leave':
            if self.check_in and self.check_out:
                self.status = 'checked_out'
            elif self.check_in and not self.check_out:
                self.status = 'checked_in'
            elif not self.check_in:
                self.status = 'not_checked_in'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} - {self.date} - {self.status}"