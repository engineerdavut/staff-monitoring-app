
from notification.utils import get_notification_service

def send_notification(user, notification_type, **kwargs):
    notification_service = get_notification_service()
    notification_service.create_notification(user, notification_type, **kwargs)