from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import logout
from django.views.generic import TemplateView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login  
from .serializers import UserSerializer
from .authrepository import AuthRepository  
from .services import UserService, EmployeeLoginService, AuthorizedLoginService
import os  
import logging

logger = logging.getLogger(__name__)


class EmployeeLoginTemplateView(TemplateView):
    template_name = 'authentication/employee_login.html'

class AuthorizedLoginTemplateView(TemplateView):
    template_name = 'authentication/authorized_login.html'

class EmployeeRegisterTemplateView(TemplateView):
    template_name = 'authentication/employee_register.html'

class AuthorizedRegisterTemplateView(TemplateView):
    template_name = 'authentication/authorized_register.html'


class EmployeeRegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            auth_repo = AuthRepository()
            user_service = UserService(auth_repo)

            try:
                user = user_service.register_employee(
                    username=serializer.validated_data['username'],
                    email=serializer.validated_data['email'],
                    password=serializer.validated_data['password']
                )
                if user:
                    login(request, user)  
                    token = user_service.generate_token(user) 
                    response_data, status_code = EmployeeLoginService.handle_login(request, user, token)
                    return Response(response_data, status=status_code)
                else:
                    return Response({"error": "Registration failed."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error registering employee: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuthorizedRegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        key = data.get('key')
        authorized_key = os.environ.get('AUTHORIZED_KEY', '')
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            auth_repo = AuthRepository()
            user_service = UserService(auth_repo)

            try:
                user = user_service.register_authorized(
                    username=serializer.validated_data['username'],
                    email=serializer.validated_data['email'],
                    password=serializer.validated_data['password'],
                    key=key,
                    authorized_key=authorized_key
                )
                if user:
                    login(request, user)  
                    token = user_service.generate_token(user) 
                    response_data, status_code = AuthorizedLoginService.handle_login(request, user, token)
                    return Response(response_data, status=status_code)
                else:
                    return Response({"error": "Registration failed."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.warning(f"Error registering authorized user: {str(e)}  {str(key)}  {str(authorized_key)}")
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BaseLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        logger.info(f"Login attempt for user: {username}")

        try:
            auth_repo = AuthRepository()
            user_service = UserService(auth_repo)
            user = user_service.authenticate_user(username, password)

            if user is not None: 
                login(request, user) 

                token = user_service.generate_token(user)
                return self.handle_successful_login(request, user, token)
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        except ValueError as e:
            logger.warning(f"Login failed for username {username}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"Unexpected error during login for {username}: {str(e)}")
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def handle_successful_login(self, request, user, token):
        raise NotImplementedError("Subclasses must implement this method")

class EmployeeLoginAPIView(BaseLoginAPIView):
    permission_classes = [AllowAny]

    def handle_successful_login(self, request, user, token):
        logger.info(f"Handling successful login for employee: {user.username}")
        response_data, status_code = EmployeeLoginService.handle_login(request, user, token)
        logger.info(f"Login response for employee {user.username}: {response_data}, status: status_code")
        return Response(response_data, status=status_code)

class AuthorizedLoginAPIView(BaseLoginAPIView):
    permission_classes = [AllowAny]

    def handle_successful_login(self, request, user, token):
        logger.info(f"Handling successful login for authorized user: {user.username}")
        response_data, status_code = AuthorizedLoginService.handle_login(request, user, token)
        logger.info(f"Login response for authorized user {user.username}: {response_data}, status: status_code")
        return Response(response_data, status=status_code)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        logout(request)
        Token.objects.filter(user=user).delete()
        logger.info(f"User {request.user.username} logged out successfully.")
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)