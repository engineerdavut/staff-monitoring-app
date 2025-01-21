from abc import ABC, abstractmethod

class INotificationRepository(ABC):


    @abstractmethod
    def get_notification(self, notification_id):

        pass

    @abstractmethod
    def get_user_notifications(self, user_id):

        pass

    @abstractmethod
    def create_notification(self, notification_data):

        pass

    @abstractmethod
    def mark_notification_as_read(self, notification_id):

        pass

    @abstractmethod
    def bulk_create_notifications(self, notification_list):

        pass
