from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import json
import logging

logger = logging.getLogger(__name__)

class EmployeeAttendanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            employee = await self.get_employee()
            employee_id = employee.id
            self.group_name = f"user_{employee_id}_employee_attendance"
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
            logger.info(f"User {self.scope['user'].id} connected to group {self.group_name}")
        except AttributeError:
            logger.error("User does not have an associated employee.")
            await self.close()
        except Exception as e:
            logger.error(f"Error during WebSocket connection: {e}")
            await self.close()

    @sync_to_async
    def get_employee(self):
        return self.scope["user"].employee

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"User disconnected from group {self.group_name}")

    async def employee_realtime_attendance_update(self, event):
        message = event.get('message')
        employee_id = event.get('id')
        logger.info(f"Received update for employee_id={employee_id} with message={message}")
        if message and employee_id:
            await self.send(text_data=json.dumps({
                'event_type': 'employee_realtime_attendance_update',
                'data': message,
                'id': employee_id  
            }))
        else:
            logger.warning("Received 'realtime_attendance_update' without message or id: %s", event)

    async def employee_attendance_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'employee_attendance_update',
            'data': event.get('data')
        }))
