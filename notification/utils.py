from .notificationrepository import NotificationRepository
from .services import NotificationService


def get_notification_repository():
     return NotificationRepository()

def get_notification_service():
     repository = get_notification_repository()
     return NotificationService(repository)