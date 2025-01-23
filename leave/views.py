from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import LeaveSerializer
from rest_framework import generics  
from .services import LeaveService
from .leaverepository import LeaveRepository
from django.core.exceptions import ValidationError as DjangoValidationError 
from .models import Leave  
from employee.employeerepository import EmployeeRepository
from rest_framework.exceptions import ValidationError
from .serializers import AuthorizedLeaveSerializer 

import logging
logger = logging.getLogger(__name__)


class BaseLeaveAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get_service(self):

        return LeaveService(
            leave_repository=self.leave_repository,
            employee_repository=self.employee_repository
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.leave_repository = LeaveRepository()
        self.employee_repository = EmployeeRepository()

class EmployeeLeaveListAPIView(BaseLeaveAPIView, generics.ListAPIView):
    serializer_class = LeaveSerializer

    def get_queryset(self):
        employee = self.request.user.employee
        leave_service = self.get_service()
        return leave_service.get_employee_leaves(employee)

class EmployeeLeaveCreateAPIView(BaseLeaveAPIView, generics.CreateAPIView):
    serializer_class = LeaveSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            employee = request.user.employee
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']
            reason = serializer.validated_data.get('reason', '')

            leave_service = self.get_service()

            try:
                leave = leave_service.request_leave(employee, start_date, end_date, reason)
                response_serializer = self.get_serializer(leave)
                headers = self.get_success_headers(response_serializer.data)
                logger.info(f"Employee {request.user.username} submitted leave request.")
                return Response({
                    "message": "Leave request submitted successfully.",
                    "data": response_serializer.data
                }, status=status.HTTP_201_CREATED, headers=headers)
            except ValidationError as ve:
                # Hata mesajını düzeltin
                error_message = ', '.join([str(e) for e in ve.detail])
                logger.warning(f"Leave request failed for {request.user.username}: {error_message}")
                return Response({'error': f"{error_message}"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                # Daha açıklayıcı bir hata mesajı döndürün
                logger.error(f"Unexpected error for {request.user.username}: {str(e)}")
                return Response({
                    'error': str(e) if str(e) else "An unexpected error occurred."
                }, status=status.HTTP_400_BAD_REQUEST)

        logger.warning(f"Leave request validation failed for {request.user.username}: {serializer.errors}")
        return Response({'error': "Invalid leave request data."}, status=status.HTTP_400_BAD_REQUEST)

class AuthorizedLeaveListAPIView(BaseLeaveAPIView, generics.ListAPIView):
    serializer_class = LeaveSerializer

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'user_type') or user.user_type != 'authorized':
            logger.warning(f"Unauthorized access attempt by {user.username}")
            return Leave.objects.none()  # Boş bir queryset döndürür
        leave_service = self.get_service()
        return leave_service.get_all_leaves()

    def list(self, request, *args, **kwargs):
        user = request.user
        if not hasattr(user, 'user_type') or user.user_type != 'authorized':
            logger.warning(f"Unauthorized access attempt by {user.username}")
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)

class AuthorizedLeaveCreateAPIView(BaseLeaveAPIView, generics.CreateAPIView):
    serializer_class = AuthorizedLeaveSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        if not hasattr(user, 'user_type') or user.user_type != 'authorized':
            logger.warning(f"Unauthorized leave creation attempt by {user.username}")
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            employee = serializer.validated_data['employee']
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']
            reason = serializer.validated_data.get('reason', '')

            leave_service = self.get_service()

            try:
                leave = leave_service.create_approved_leave(employee, start_date, end_date, reason)
                response_serializer = self.get_serializer(leave)
                headers = self.get_success_headers(response_serializer.data)
                logger.info(f"Authorized user {user.username} created an approved leave for employee ID {employee.id}.")
                return Response({
                    "message": "Leave approved and created successfully.",
                    "data": response_serializer.data
                }, status=status.HTTP_201_CREATED, headers=headers)
            except ValidationError as ve:
                logger.warning(f"Authorized leave creation failed for user {user.username}: {ve.detail}")
                return Response({'error': ve.detail}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.warning(f"Authorized leave creation failed for user {user.username}: {str(e)}")
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        logger.warning(f"Leave request validation failed for authorized user {user.username}: {serializer.errors}")
        return Response({'error': "Invalid leave request data."}, status=status.HTTP_400_BAD_REQUEST)

class LeaveActionAPIView(BaseLeaveAPIView, generics.GenericAPIView):

    def post(self, request, pk, action):
        user = request.user
        if not hasattr(user, 'user_type') or user.user_type != 'authorized':
            logger.warning(f"Unauthorized leave action attempt by {user.username}")
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        if action not in ['approve', 'reject']:
            return Response({'error': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

        leave_service = self.get_service()

        try:
            if action == 'approve':
                result = leave_service.approve_leave(pk)
                if result['status'] == 'rejected':
                    serializer = LeaveSerializer(result['leave'])
                    return Response({
                        "message": result['message'],
                        "leave": serializer.data
                    }, status=status.HTTP_200_OK)
                elif result['status'] == 'approved':
                    serializer = LeaveSerializer(result['leave'])
                    return Response({
                        "message": result['message'],
                        "leave": serializer.data
                    }, status=status.HTTP_200_OK)
            elif action == 'reject':
                leave = leave_service.reject_leave(pk)
                logger.info(f"Leave {pk} rejected by {user.username}.")
                serializer = LeaveSerializer(leave)
                return Response({
                    "message": "Leave rejected successfully.",
                    "leave": serializer.data
                }, status=status.HTTP_200_OK)
        except DjangoValidationError as ve:
            error_message = ' '.join(ve.messages)
            logger.warning(f"Leave action failed for {user.username}: {error_message}")
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Error processing leave action {action}: {e}")
            return Response({'error': 'Internal server error.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CancelLeaveAPIView(BaseLeaveAPIView, generics.GenericAPIView):

    def post(self, request, pk):
        employee = request.user.employee
        leave_service = self.get_service()

        try:
            leave = leave_service.cancel_leave(pk)
            logger.info(f"Employee {request.user.username} cancelled leave ID {pk}.")
            return Response({"message": "Leave request cancelled successfully."}, status=status.HTTP_200_OK)
        except ValidationError as ve:
            logger.warning(f"Failed to cancel leave ID {pk}: {ve.detail}")
            return Response({'error': ve.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.warning(f"Failed to cancel leave ID {pk}: {str(e)}")
            return Response({'error': "An unexpected error occurred."}, status=status.HTTP_400_BAD_REQUEST)