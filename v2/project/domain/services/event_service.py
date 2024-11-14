# domain/services/event_service.py

from v2.project.domain.entities.event import Event
from v2.project.domain.ports.event_repository import EventRepository
from v2.project.domain.ports.user_repository import UserRepository


class EventService:
    def __init__(self, event_repo: EventRepository, user_repo: UserRepository):
        self.event_repo = event_repo
        self.user_repo = user_repo

    def create_event(self, user_id, name, description, place, date_time, participant_limit, host_name) -> int:
        user = self.user_repo.get_user(user_id)
        if user is None or (not user.is_verified and len(self.event_repo.get_user_events(user_id)) > 2):
            raise PermissionError("User is not verified or has reached the limit for creating events")
        event = Event(None, name, description, place, date_time, participant_limit, user_id, host_name,0)
        return self.event_repo.add_event(event)

    def get_event(self, event_id):
        return self.event_repo.get_event(event_id)

    def get_upcoming_events(self):
        return self.event_repo.get_upcoming_events()

    def register_user_for_event(self, user_id, event_id):
        event = self.event_repo.get_event(event_id)
        if event.participant_limit is None or event.participant_count < event.participant_limit:
            event.participant_count += 1
            self.event_repo.update_event(event)
            self.user_repo.register_user_for_event(user_id, event_id)
            return True
        return False

    def delete_event(self, event_id):
        event = self.event_repo.get_event(event_id)
        if event:
            self.event_repo.delete_event(event_id)
            return True
        return False

    def get_user_events(self, user_id):
        return self.event_repo.get_user_events(user_id)

    def get_event_participants(self, event_id: int) -> int:
        return self.event_repo.get_event_participants(event_id)
