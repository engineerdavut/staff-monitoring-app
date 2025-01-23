from django.core.management.base import BaseCommand
from django.conf import settings
from celery import Celery
from celery.exceptions import TimeoutError

class Command(BaseCommand):
    help = 'Checks if Celery is running and configured correctly'

    def handle(self, *args, **options):
        self.stdout.write('Checking Celery configuration...')


        self.stdout.write(f'CELERY_BROKER_URL: {settings.CELERY_BROKER_URL}')


        app = Celery('employee_tracking_system')
        app.conf.broker_url = settings.CELERY_BROKER_URL
        try:
            app.control.ping(timeout=5)
            self.stdout.write(self.style.SUCCESS('Celery broker connection successful!'))
        except TimeoutError:
            self.stdout.write(self.style.ERROR('Celery broker connection failed!'))


        try:
            active_workers = app.control.inspect().active()
            if active_workers:
                self.stdout.write(self.style.SUCCESS(f'Active Celery workers: {", ".join(active_workers.keys())}'))
            else:
                self.stdout.write(self.style.WARNING('No active Celery workers found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to inspect Celery workers: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Celery check completed'))