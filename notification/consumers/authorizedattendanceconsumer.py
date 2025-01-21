from .base import BaseConsumer
import json
import logging

logger = logging.getLogger(__name__)

class AuthorizedAttendanceConsumer(BaseConsumer):
    def get_group_name(self):
        return 'authorized_attendance'

    def get_update_type(self):
        return 'attendance_update'

    async def realtime_attendance_update(self, event):
        message = event.get('message')
        if message:
            await self.send(text_data=json.dumps({
                'type': 'realtime_attendance_update',
                'data': message
            }))
        else:
            logger.warning("Received 'realtime_attendance_update' without message: %s", event)