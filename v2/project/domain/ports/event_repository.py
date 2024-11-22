# domain/ports/event_repository.py

from abc import ABC, abstractmethod
from v2.project.domain.entities.event import Event

class EventRepository(ABC):
    @abstractmethod
    def add_event(self, event: Event) -> int:
        pass

    @abstractmethod
    def get_event(self, event_id: int) -> Event:
        pass

    @abstractmethod
    def get_upcoming_events(self):
        pass

    @abstractmethod
    def delete_event(self, event_id: int):
        pass

    @abstractmethod
    def update_event(self, event: Event):
        pass

    @abstractmethod
    def get_user_events(self, user_id: int):
        pass

    @abstractmethod
    def get_event_participants(self, event_id: int) -> int:
        pass

    def get_user_registrations(self, user_id):
        pass

    def delete_register(self, user_id, event_id):
        pass

    def get_user_registration(self, user_id, event_id):
        pass
