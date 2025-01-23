from django.db import models
from datetime import timedelta
from django.contrib.auth import get_user_model
from .managers import EmployeeManager  
from django.utils import timezone

class Employee(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    annual_leave = models.IntegerField(default=15)
    remaining_leave = models.DurationField(default=timedelta(days=15))  
    total_lateness = models.DurationField(default=timedelta)
    total_work_duration = models.DurationField(default=timedelta)
    registration_date = models.DateField(auto_now_add=True) 

    objects = EmployeeManager() 

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"