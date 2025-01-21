from django.shortcuts import get_object_or_404
from .models import Notification
from .inotificationrepository import INotificationRepository

class NotificationRepository(INotificationRepository):

    def get_notification(self, notification_id):
        return get_object_or_404(Notification, id=notification_id)

    def get_user_notifications(self, user_id):
        return Notification.objects.filter(user_id=user_id).order_by('-created_at')

    def create_notification(self, notification_data):
        return Notification.objects.create(**notification_data)

    def mark_notification_as_read(self, notification_id):
        notification = get_object_or_404(Notification, id=notification_id)
        notification.is_read = True
        notification.save()
        return notification

    def bulk_create_notifications(self, notification_list):
        return Notification.objects.bulk_create(notification_list)
