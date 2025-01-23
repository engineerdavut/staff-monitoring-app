from abc import ABC, abstractmethod

class IAuthRepository(ABC):
    @abstractmethod
    def create_user(self, username, email, password, user_type):
        pass

    @abstractmethod
    def authenticate_user(self, username, password):
        pass

    @abstractmethod
    def get_user_by_id(self, user_id):
        pass