from channels.db import database_sync_to_async
from django.core.serializers.json import DjangoJSONEncoder
import json
from .base import BaseConsumer
from ..models import Notification

class NotificationConsumer(BaseConsumer):
    def get_group_name(self):
        return f"user_{self.user.id}_notifications"

    def get_update_type(self):
        return 'notification'

    async def connect(self):
        await super().connect()
        if self.user.is_authenticated:
            await self.send_existing_notifications()

    @database_sync_to_async
    def get_existing_notifications(self):
        return list(Notification.objects.filter(user=self.user, is_read=False).values(
            'id', 'message', 'created_at', 'type', 'severity'
        ))

    async def send_existing_notifications(self):
        notifications = await self.get_existing_notifications()
        if notifications:
            await self.send(text_data=json.dumps({
                'type': 'existing_notifications',
                'notifications': notifications
            }, cls=DjangoJSONEncoder))
