import time
import os
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
import redis

class Command(BaseCommand):
    help = 'Waits for database and Redis to be available'

    def add_arguments(self, parser):
        parser.add_argument('service', type=str, help="Service to wait for: 'db' or 'redis'")
        parser.add_argument('--sleep_interval', type=int, default=1, help="Sleep interval between retries in seconds")
        parser.add_argument('--max_retries', type=int, default=60, help="Maximum number of retries")

    def handle(self, *args, **options):
        service = options['service']
        sleep_interval = options['sleep_interval']
        max_retries = options['max_retries']

        self.stdout.write(f'Waiting for {service}...')

        if service == 'db':
            self.wait_for_db(sleep_interval, max_retries)
        elif service == 'redis':
            self.wait_for_redis(sleep_interval, max_retries)
        else:
            self.stdout.write(self.style.ERROR(f'Unknown service: {service}'))

    def wait_for_db(self, sleep_interval, max_retries):
        retries = 0
        while retries < max_retries:
            try:
                connections['default'].ensure_connection()
                self.stdout.write(self.style.SUCCESS('Database is available!'))
                return
            except OperationalError:
                retries += 1
                self.stdout.write(f'Database unavailable, waiting {sleep_interval} second(s)... ({retries}/{max_retries})')
                time.sleep(sleep_interval)
        
        self.stdout.write(self.style.ERROR('Failed to connect to the database after maximum retries!'))
        exit(1)

    def wait_for_redis(self, sleep_interval, max_retries):
        retries = 0
        redis_url = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
        while retries < max_retries:
            try:
                redis_client = redis.from_url(redis_url)
                redis_client.ping()
                self.stdout.write(self.style.SUCCESS('Redis is available!'))
                return
            except redis.exceptions.ConnectionError:
                retries += 1
                self.stdout.write(f'Redis unavailable, waiting {sleep_interval} second(s)... ({retries}/{max_retries})')
                time.sleep(sleep_interval)
        
        self.stdout.write(self.style.ERROR('Failed to connect to Redis after maximum retries!'))
        exit(1)
