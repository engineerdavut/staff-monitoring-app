import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .services import NotificationService
from .notificationrepository import NotificationRepository
from .serializers import NotificationSerializer

logger = logging.getLogger(__name__)

# Instantiating Repository and Service (constructor injection is generally recommended,
# but we are directly instantiating here for simplicity).
notification_repository = NotificationRepository()
notification_service = NotificationService(notification_repository)

class NotificationListView(APIView):
    """
    1. Endpoint for listing the notifications of a user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"User {request.user.username} is fetching their notifications.")
        notifications = notification_service.fetch_notifications(request.user)
        if notifications is None:
            return Response({"detail": "An error occurred while fetching notifications."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationCreateView(APIView):
    """
    2. Endpoint for creating a new notification.
    Example: POST /notifications/create/
    Body: {
       "notification_type": "LOW_LEAVE_BALANCE",
       "severity": "warning",
       "type": "temporary",
       "send_realtime": true,
       ...
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info(f"Creating a new notification for user {request.user.username}.")
        notification_type = request.data.get("notification_type")
        if not notification_type:
            return Response({"detail": "The notification_type field is required."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        notification = notification_service.create_notification(request.user, notification_type, **request.data)
        if not notification:
            return Response({"detail": "Failed to create notification, please enter a valid type."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NotificationMarkReadView(APIView):
    """
    3. Endpoint for marking a notification as read.
    Example: POST /notifications/mark-read/<pk>/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        logger.info(f"User {request.user.username} requested to mark notification {pk} as read.")
        notification = notification_service.mark_notification_as_read(request.user, pk)
        if not notification:
            return Response({"detail": "Notification not found or you do not have permission."},
                            status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": f"Notification {pk} has been marked as read."},
                        status=status.HTTP_200_OK)



