# domain/services/notification_service.py

import telebot
from datetime import datetime, timedelta
from v2.project.domain.ports.event_repository import EventRepository
from v2.project.domain.ports.user_repository import UserRepository


class NotificationService:
    def __init__(self, bot: telebot.TeleBot, event_repo: EventRepository, user_repo: UserRepository):
        self.bot = bot
        self.event_repo = event_repo
        self.user_repo = user_repo

    def send_reminders(self):
        # Получить список всех предстоящих мероприятий
        events = self.event_repo.get_upcoming_events()
        for event in events:
            event_date = datetime.strptime(event.date_time, '%Y-%m-%d %H:%M')
            # Проверить, что мероприятие через день
            if event_date - timedelta(days=1) <= datetime.now() < event_date:
                participants = self.event_repo.get_event_participants(event.id)
                for user_id in participants:
                    user = self.user_repo.get_user(user_id)
                    if user:
                        self.bot.send_message(user.user_id, f"Напоминание: завтра состоится мероприятие '{event.name}'")

    def notify_cancellation(self, event_id):
        event = self.event_repo.get_event(event_id)
        participants = self.event_repo.get_event_participants(event_id)
        for user_id in participants:
            user = self.user_repo.get_user(user_id)
            if user:
                self.bot.send_message(user.user_id, f"Мероприятие '{event.name}' было отменено организатором.")
