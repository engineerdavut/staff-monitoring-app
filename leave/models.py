from django.db import models
from django.core.exceptions import ValidationError
from .managers import LeaveManager
from employee.models import Employee

class Leave(models.Model):
    PENDING = 'Pending'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'
    CANCELLED = 'Cancelled'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (CANCELLED, 'Cancelled'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = LeaveManager()  

    def clean(self):
       
        if self.start_date > self.end_date:
            raise ValidationError("End date must be after start date.")

        if self.status in [self.PENDING, self.APPROVED]:
            overlapping_leaves = Leave.objects.filter(
                employee=self.employee,
                status__in=[self.PENDING, self.APPROVED],
            ).exclude(id=self.id).filter(
                start_date__lte=self.end_date,
                end_date__gte=self.start_date
            )
            if overlapping_leaves.exists():
                conflicting_leaves = overlapping_leaves.values_list('start_date', 'end_date')
                conflict_dates = ", ".join([f"{start} to {end}" for start, end in conflicting_leaves])
                raise ValidationError(f"This leave request overlaps with existing leaves: {conflict_dates}.")

    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Employee {self.employee.user.username} - {self.start_date} to {self.end_date}"