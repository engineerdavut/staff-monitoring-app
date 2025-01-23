from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError  

class WorkingHours(models.Model):
    start_time = models.TimeField(default=timezone.datetime.strptime('08:00', '%H:%M').time())
    end_time = models.TimeField(default=timezone.datetime.strptime('18:00', '%H:%M').time())

    class Meta:
        app_label = 'employee_tracking_system'

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_current(cls):
        return cls.objects.first() or cls.objects.create()