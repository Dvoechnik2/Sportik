# main.py

from domain.services.event_service import EventService
from domain.services.notification_service import NotificationService
from adapters.db.sqlite_event_repository import SQLiteEventRepository
from adapters.db.sqlite_user_repository import SQLiteUserRepository
from adapters.api.telegram_bot import TelegramBotAdapter
import telebot

from v2.project.domain.ports.user_repository import UserRepository

# Путь к базе данных
DB_PATH = "data/events.db"
TOKEN = "7473067108:AAERYtQit6t6Yu4pfTBdVMp3CNSSDIN9PhU"

# Инициализация репозиториев для работы с БД
event_repo = SQLiteEventRepository(DB_PATH)
user_repo = SQLiteUserRepository(DB_PATH)

# Создание сервисов
event_service = EventService(event_repo, user_repo)
notification_service = NotificationService(telebot.TeleBot(TOKEN), event_repo, user_repo)

# Инициализация бота с нужными сервисами
bot = TelegramBotAdapter(TOKEN, event_service, notification_service, user_repo)

# Запуск бота
bot.start()
