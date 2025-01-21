from channels.db import database_sync_to_async
from .notification import NotificationConsumer

class AuthorizedNotificationConsumer(NotificationConsumer):
    async def connect(self):
        await super().connect()
        if self.user.is_authenticated:
            permissions = await self.get_user_permissions()
            if 'employee.can_manage_employees' in permissions:
                await self.channel_layer.group_add(
                    'authorized_notifications',
                    self.channel_name
                )

    async def disconnect(self, close_code):
        await super().disconnect(close_code)
        if self.user.is_authenticated:
            permissions = await self.get_user_permissions()
            if 'employee.can_manage_employees' in permissions:
                await self.channel_layer.group_discard(
                    'authorized_notifications',
                    self.channel_name
                )

    @database_sync_to_async
    def get_user_permissions(self):
        return list(self.user.get_all_permissions())

    async def authorized_update(self, event):
        await self.send_update(event)