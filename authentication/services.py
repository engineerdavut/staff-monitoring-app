from rest_framework.authtoken.models import Token
from rest_framework import status
from .iauthrepository import IAuthRepository
from employee.models import Employee
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, auth_repository: IAuthRepository):
        self.auth_repository = auth_repository

    def register_employee(self, username, email, password):
        try:
            user = self.auth_repository.create_user(
                username=username, 
                email=email, 
                password=password, 
                user_type='employee'
            )
            Employee.objects.create(user=user)
            logger.info(f"Employee profile created for user: {username}")
            return user
        except Exception as e:
            logger.error(f"Error registering employee: {str(e)}")
            raise

    def register_authorized(self, username, email, password, key, authorized_key):
        if key != authorized_key:
            logger.warning(f"Invalid authorization key attempt for user: {username}")
            raise ValueError("Invalid authorization key")

        try:
            user = self.auth_repository.create_user(
                username=username, 
                email=email, 
                password=password, 
                user_type='authorized'
            )
            logger.info(f"Authorized user created: {username}")
            return user
        except Exception as e:
            logger.error(f"Error registering authorized user: {str(e)}  {str(key)}  {str(authorized_key)}")
            raise

    def authenticate_user(self, username, password):
        user = self.auth_repository.authenticate_user(username, password)
        if user is None:
            raise ValueError("Invalid credentials")
        return user

    def generate_token(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        return token.key

    @staticmethod
    def handle_login(request, user, token, expected_user_type, redirect_url):
        if user.user_type != expected_user_type:
            return {"error": "Invalid user type"}, status.HTTP_400_BAD_REQUEST

        response_data = {
            "message": f"{expected_user_type.capitalize()} login successful",
            "token": token,
            "username": user.username,
            "redirect": redirect_url
        }

        if expected_user_type == 'employee':
            try:
                employee_id = user.employee.id
                response_data['employee_id'] = employee_id
            except AttributeError:
                response_data['employee_id'] = None

        return response_data, status.HTTP_200_OK

class EmployeeLoginService(UserService):
    @staticmethod
    def handle_login(request, user, token):
        return UserService.handle_login(request, user, token, 'employee', "/employee/employee-dashboard/")

class AuthorizedLoginService(UserService):
    @staticmethod
    def handle_login(request, user, token):
        return UserService.handle_login(request, user, token, 'authorized', "/employee/authorized-dashboard/")