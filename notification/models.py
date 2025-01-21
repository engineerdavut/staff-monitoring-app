from django.db import models
from django.conf import settings

class Notification(models.Model):
    TYPE_CHOICES = [
        ('persistent', 'Persistent'),
        ('temporary', 'Temporary'),
    ]

    SEVERITY_CHOICES = [
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('info', 'Info'),
        ('danger', 'Danger'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='temporary')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='info')

    def __str__(self):
        return f"{self.user} - {self.created_at}"


