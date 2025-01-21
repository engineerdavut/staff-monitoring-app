from .base import BaseConsumer
import json 
import logging  

logger = logging.getLogger(__name__)  
 
class AttendanceConsumer(BaseConsumer):
    def get_group_name(self):
        return f"user_{self.user.id}_attendance"

    def get_update_type(self):
        return 'attendance'


    async def receive(self, text_data=None, bytes_data=None):
        logger.info(f"Ignoring incoming message: {text_data}")


    async def attendance_update(self, event):
        await self.send_update(event)

