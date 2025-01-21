from django.urls import path
from .views import (
    EmployeeRegisterAPIView, AuthorizedRegisterAPIView,
    EmployeeLoginAPIView, AuthorizedLoginAPIView, 
    EmployeeRegisterTemplateView,AuthorizedRegisterTemplateView,
    EmployeeLoginTemplateView,AuthorizedLoginTemplateView, 
    LogoutAPIView
)

urlpatterns = [
    path('login/employee/', EmployeeLoginTemplateView.as_view(), name='employee_login'),
    path('login/authorized/', AuthorizedLoginTemplateView.as_view(), name='authorized_login'),
    path('register/employee/', EmployeeRegisterTemplateView.as_view(), name='employee_register'),
    path('register/authorized/', AuthorizedRegisterTemplateView.as_view(), name='authorized_register'),
    path('api/login/employee/', EmployeeLoginAPIView.as_view(), name='employee_login_api'),
    path('api/login/authorized/', AuthorizedLoginAPIView.as_view(), name='authorized_login_api'),
    path('api/register/employee/', EmployeeRegisterAPIView.as_view(), name='employee_register_api'),
    path('api/register/authorized/', AuthorizedRegisterAPIView.as_view(), name='authorized_register_api'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
]
