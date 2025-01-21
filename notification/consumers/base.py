import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging

logger = logging.getLogger(__name__)


class BaseConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            await self.channel_layer.group_add(
                self.get_group_name(),
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(
                self.get_group_name(),
                self.channel_name
            )

    def get_group_name(self):
        raise NotImplementedError("Subclasses must implement get_group_name()")

    async def send_update(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': self.get_update_type(),
            'data': message
        }))

    def get_update_type(self):
        raise NotImplementedError("Subclasses must implement get_update_type()")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message')
            if message:
                await self.channel_layer.group_send(
                    self.get_group_name(),
                    {
                        'type': 'send_update',
                        'message': message
                    }
                )
            else:
                logger.warning("Received message without 'message' key: %s", text_data_json)
        except json.JSONDecodeError:
            logger.error("Received invalid JSON: %s", text_data)
        except Exception as e:
            logger.error(f"Error in receive method: {e}")

