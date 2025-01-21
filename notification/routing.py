from django.urls import re_path
from .consumers.notification import NotificationConsumer
from .consumers.attendance import AttendanceConsumer
from .consumers.authorized import AuthorizedNotificationConsumer
from .consumers.employeeattendanceconsumer import EmployeeAttendanceConsumer
from .consumers.authorizedattendanceconsumer import AuthorizedAttendanceConsumer

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
    re_path(r'ws/attendance/$', AttendanceConsumer.as_asgi()),
    re_path(r'ws/authorized_notifications/$', AuthorizedNotificationConsumer.as_asgi()),
    re_path(r'ws/employee_attendance/$', EmployeeAttendanceConsumer.as_asgi()),
    re_path(r'ws/authorized_attendance/$', AuthorizedAttendanceConsumer.as_asgi()),
]