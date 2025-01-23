import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_tracking_system.settings')

app = Celery('employee_tracking_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_url = os.environ.get('REDIS_URL', 'redis://redis:6379/0')

app.conf.beat_schedule = {
    'update-real-time-attendance': {
        'task': 'attendance.tasks.update_real_time_attendance',
        'schedule': crontab(minute='*/5', hour='0-19',day_of_week='1-5'),  
    },
    'calculate-monthly-total-work-duration': {
        'task': 'attendance.tasks.generate_monthly_report_task',
        'schedule': crontab(hour=0, minute=0, day_of_month='1'),
    },
    'reset-annual-leave': {
        'task': 'employee.tasks.reset_annual_leave',
        'schedule': crontab(0, 0, day_of_month='1', month_of_year='1'),  
    },
    'check-low-leave-balance': {
        'task': 'employee.tasks.check_low_leave_balance',
        'schedule': crontab(hour=9, minute=0),  
    },
    'notify_no_check_in_for_today': {
        'task': 'employee.tasks.notify_no_check_in_for_today',
        'schedule': crontab(hour=10, minute=0),  
    },
    'update_employee_totals': {
        'task': 'employee.tasks.update_employee_totals',
        'schedule': crontab(hour=19, minute=00),
    },
}

app.autodiscover_tasks()