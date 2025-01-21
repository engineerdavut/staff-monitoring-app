from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin
from .views import home 

schema_view = get_schema_view(
    openapi.Info(
        title="Employee Tracking API",
        default_version='v1',
        description="API for Employee Tracking System",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# API versioning namespace
api_v1_patterns = [                    
    path('leave/', include('leave.urls')),
    path('notification/', include('notification.urls')),  
]

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', home, name='home'),
    path('auth/', include('authentication.urls')),
    path('employee/', include('employee.urls')),
    path('api/v1/', include((api_v1_patterns, 'api_v1'))),
    path('api/v1/attendance/', include('attendance.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
