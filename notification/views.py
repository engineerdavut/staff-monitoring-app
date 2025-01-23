from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .services import NotificationService
from .notificationrepository import NotificationRepository
from .serializers import NotificationSerializer

import logging

logger = logging.getLogger(__name__)

notification_repository = NotificationRepository()
notification_service = NotificationService(notification_repository)

class NotificationListView(APIView):
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
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        logger.info(f"User {request.user.username} requested to mark notification {pk} as read.")
        notification = notification_service.mark_notification_as_read(request.user, pk)
        if not notification:
            return Response({"detail": "Notification not found or you do not have permission."},
                            status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": f"Notification {pk} has been marked as read."},
                        status=status.HTTP_200_OK)