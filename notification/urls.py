from django.urls import path
from django.urls import path
from .views import (
    NotificationListView,
    NotificationCreateView,
    NotificationMarkReadView,
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification_list'),
    path('create/', NotificationCreateView.as_view(), name='notification_create'),
    path('mark-read/<int:pk>/', NotificationMarkReadView.as_view(), name='notification_mark_read'),
]

