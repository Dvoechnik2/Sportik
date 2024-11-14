# domain/ports/user_repository.py

from abc import ABC, abstractmethod
from v2.project.domain.entities.user import User

class UserRepository(ABC):
    @abstractmethod
    def get_user(self, user_id: int) -> User:
        pass

    @abstractmethod
    def add_user(self, user: User):
        pass

    @abstractmethod
    def verify_user_phone(self, user_id: int, phone: str):
        pass

    @abstractmethod
    def register_user_for_event(self, user_id: int, event_id: int):
        pass
