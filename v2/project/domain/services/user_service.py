# domain/services/user_service.py

from v2.project.domain.entities.event import Event
from v2.project.domain.ports.event_repository import EventRepository
from v2.project.domain.ports.user_repository import UserRepository


class UserService:
    def __init__(self, event_repo: EventRepository, user_repo: UserRepository):
        self.event_repo = event_repo
        self.user_repo = user_repo

    def register_user_for_event(self, user_id: int, event_id: int):
        return self.user_repo.register_user_for_event(user_id, event_id)
