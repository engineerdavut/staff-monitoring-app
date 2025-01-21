# notification/tasks.py
import logging
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

@shared_task
def send_notification(user_id, notification_type, **kwargs):
    try:
        User = get_user_model()
        user = User.objects.get(pk=user_id)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{user_id}",
            {
                "type": "notification.send",
                "notification_type": notification_type,
                "data": kwargs,
            }
        )
        logger.info(f"Real-time notification sent to user {user_id}, type: {notification_type}")
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found.")
    except Exception as e:
        logger.error(f"Error sending notification to user {user_id}: {e}")