# notification/services.py
import logging
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .constants import NOTIFICATION_MESSAGES, NOTIFICATION_DEFAULTS
from .inotificationrepository import INotificationRepository
from .tasks import send_notification

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Manages business logic related to notifications.
    """

    def __init__(self, notification_repository: INotificationRepository):
        self._repository = notification_repository

    def _prepare_notification(self, notification_type, **kwargs):
        """
        Prepares the notification message and data (type, severity)
        before creating the notification object.
        """
        template = NOTIFICATION_MESSAGES.get(notification_type)
        if not template:
            logger.warning(f"Notification type '{notification_type}' is not defined.")
            return None, None

        # Hazır mesaj şablonunu kwargs verileriyle formatla
        message = template.format(**kwargs)

        # NOTIFICATION_DEFAULTS içinden varsayılan tip/severity değerlerini al
        defaults = NOTIFICATION_DEFAULTS.get(notification_type, {})

        notification_data = {
            "message": message,
            "type": kwargs.get("type", defaults.get("type", "temporary")),
            "severity": kwargs.get("severity", defaults.get("severity", "info")),
        }
        return message, notification_data

    def create_notification(self, user, notification_type, **kwargs):
        """
        Creates a single notification. Optionally sends a real-time message via Celery.
        """
        message, notification_data = self._prepare_notification(notification_type, **kwargs)
        if not message:
            return None

        # Kullanıcı objesini notification_data'ya ekle
        notification_data["user"] = user

        # Repository yardımıyla veritabanında kaydet
        notification = self._repository.create_notification(notification_data)

        # İstenirse Celery ile real-time notification gönder
        if kwargs.get("send_realtime", True):
            send_notification.delay(user.id, notification_type, **kwargs)

        logger.info(f"Notification created for user {user.username}: {message}")
        return notification

    def fetch_notifications(self, user, notification_type=None):
        """
        Fetches notifications for a specific user, optionally filtered by type.
        """
        try:
            notifications = self._repository.get_user_notifications(user.id)
            if notification_type:
                notifications = notifications.filter(type=notification_type)
            return notifications
        except Exception as e:
            logger.error(f"Error fetching notifications for user {user.username}: {str(e)}")
            return None

    def mark_notification_as_read(self, user, pk):
        """
        Marks a notification as read if it belongs to the given user.
        """
        try:
            notification = self._repository.get_notification(pk)
            if notification.user.id != user.id:
                logger.warning(
                    f"User {user.username} attempted to mark notification {pk} as read without permission."
                )
                return None

            return self._repository.mark_notification_as_read(pk)
        except Exception as e:
            logger.error(f"Error marking notification {pk} as read for user {user.username}: {str(e)}")
            return None

    @transaction.atomic
    def bulk_create_notifications(self, users, notification_type, **kwargs):
        """
        Creates notifications in bulk for multiple users.
        """
        message, notification_data = self._prepare_notification(notification_type, **kwargs)
        if not message:
            return False

        notification_list = []
        for user in users:
            data = {"user": user, **notification_data}
            notification_list.append(self._repository.create_notification(data))

        # if real-time websocket sending is needed
        if kwargs.get("send_realtime", True):
            for user in users:
                send_notification.delay(user.id, notification_type, **kwargs)

        logger.info(f"Bulk notifications created for {len(users)} users.")
        return True