from django.contrib.auth import authenticate
from django.db import transaction
from .models import User
from .iauthrepository import IAuthRepository 

class AuthRepository(IAuthRepository):
    def create_user(self, username, email, password, user_type):
        with transaction.atomic():
            return User.objects.create_user(username=username, email=email, password=password, user_type=user_type)

    def authenticate_user(self, username, password):
        return authenticate(username=username, password=password)

    def get_user_by_id(self, user_id):
        return User.objects.filter(id=user_id).first()

    def get_user_type(self, user):
        return getattr(user, 'user_type', None)