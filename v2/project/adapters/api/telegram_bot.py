# adapters/api/telegram_bot.py

import telebot
from telebot import types

from v2.project.domain.ports.user_repository import UserRepository
from v2.project.domain.services.event_service import EventService
from v2.project.domain.services.notification_service import NotificationService
from v2.project.domain.entities.user import User


class TelegramBotAdapter:
    def __init__(self, token, event_service: EventService, notification_service: NotificationService, user_repo: UserRepository):
        self.bot = telebot.TeleBot(token)
        self.event_service = event_service
        self.notification_service = notification_service
        self.user_repo = user_repo

    def save_user_phone(self, message, user_id, phone_number):
        """Сохраняем номер телефона пользователя в базе данных."""
        # Проверяем, существует ли пользователь в базе данных
        user = self.user_repo.get_user(user_id)
        if user:
            # Обновляем номер телефона
            self.user_repo.verify_user_phone(user_id, phone_number)
        else:
            # Если пользователя нет в базе данных, добавляем нового
            self.user_repo.add_user(User(user_id, message.from_user.first_name, phone_number))

    def start(self):
        @self.bot.message_handler(commands=['start', 'menu'])
        def handle_start(message):
            # Приветственное сообщение и кнопки
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Создать мероприятие")
            btn2 = types.KeyboardButton("Посмотреть мероприятия")
            btn3 = types.KeyboardButton("Мои мероприятия")
            markup.add(btn1, btn2, btn3)

            self.bot.send_message(
                message.chat.id,
                f"Привет, {message.from_user.first_name}! Чем могу помочь?",
                reply_markup=markup
            )

        @self.bot.message_handler(func=lambda message: message.text == "Создать мероприятие")
        def handle_create_event(message):
            user = self.user_repo.get_user(message.from_user.id)
            if user is None:
                self.user_repo.add_user(User(message.chat.id, message.from_user.first_name))
            if (not user.is_verified and len(self.event_service.get_user_events(user.user_id)) >= 2):
                self.bot.send_message(message.chat.id,
                                      "Вы не можете создать больше двух мероприятия. Подтвердите свой номер телефона "
                                      "с помощью команды /verify.")
            else:
                self.bot.send_message(message.chat.id, "Введите название мероприятия:")
                self.bot.register_next_step_handler(message, self.create_event_name)

        @self.bot.message_handler(func=lambda message: message.text == "Посмотреть мероприятия")
        def handle_view_events(message):
            events = self.event_service.get_upcoming_events()
            if not events:
                self.bot.send_message(message.chat.id, "Нет предстоящих мероприятий.")
            else:
                for event in events:
                    markup = types.InlineKeyboardMarkup()
                    btn_details = types.InlineKeyboardButton("Подробнее", callback_data=f"details_{event.id}")
                    markup.add(btn_details)
                    self.bot.send_message(
                        message.chat.id,
                        f"Мероприятие: {event.name}\nМесто: {event.place}\nДата: {event.date_time}",
                        reply_markup=markup
                    )

        @self.bot.message_handler(func=lambda message: message.text == "Мои мероприятия")
        def handle_my_events(message):
            user_id = message.from_user.id
            user_events = self.event_service.get_user_events(user_id)
            if not user_events:
                self.bot.send_message(message.chat.id, "У вас нет зарегистрированных мероприятий.")
            else:
                for event in user_events:
                    markup = types.InlineKeyboardMarkup()
                    btn_cancel = types.InlineKeyboardButton("Отменить", callback_data=f"cancel_{event.id}")
                    markup.add(btn_cancel)
                    self.bot.send_message(
                        message.chat.id,
                        f"Мероприятие: {event.name}\nДата: {event.date_time}\nСтатус: {event.status}",
                        reply_markup=markup
                    )


        @self.bot.message_handler(commands=['verify'])
        def handle_verify(message):
            # Кнопка для запроса номера телефона
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn = types.KeyboardButton("Подтвердить номер", request_contact=True)
            markup.add(btn)
            self.bot.send_message(message.chat.id, "Пожалуйста, подтвердите ваш номер телефона:", reply_markup=markup)

        @self.bot.message_handler(content_types=['contact'])
        def handle_contact(message):
            # Получение и сохранение номера телефона
            user_phone = message.contact.phone_number
            user_id = message.chat.id

            self.save_user_phone(message, user_id, user_phone)

            self.bot.send_message(message.chat.id, f"Ваш номер {user_phone} подтвержден успешно!")

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

            btn1 = types.KeyboardButton("Создать мероприятие")
            btn2 = types.KeyboardButton("Посмотреть мероприятия")
            btn3 = types.KeyboardButton("Мои мероприятия")
            markup.add(btn1, btn2, btn3)
            self.bot.send_message(
                message.chat.id,
                f"Ну что, {message.from_user.first_name}, продолжим?",
                reply_markup=markup
            )

        # Обработка кнопки "Подробнее" для каждого мероприятия
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("details_"))
        def handle_event_details(call):
            event_id = int(call.data.split("_")[1])
            event = self.event_service.get_event(event_id)
            if event:
                markup = types.InlineKeyboardMarkup()
                btn_register = types.InlineKeyboardButton("Зарегистрироваться", callback_data=f"register_{event.id}")
                markup.add(btn_register)
                self.bot.send_message(
                    call.message.chat.id,
                    f"Мероприятие: {event.name}\nОписание: {event.description}\nМесто: {event.place}\nДата: {event.date_time}",
                    reply_markup=markup
                )
            else:
                self.bot.send_message(call.message.chat.id, "Мероприятие не найдено.")

        # Обработка регистрации на мероприятие
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("register_"))
        def handle_register(call):
            event_id = int(call.data.split("_")[1])
            user_id = call.message.chat.id
            success = self.event_service.register_user_for_event(user_id, event_id)
            if success:
                self.bot.send_message(call.message.chat.id, "Вы успешно зарегистрировались на мероприятие!")
            else:
                self.bot.send_message(call.message.chat.id, "Извините, регистрация на это мероприятие невозможна.")

        # Обработка отмены мероприятия
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_"))
        def handle_cancel(call):
            event_id = int(call.data.split("_")[1])
            user_id = call.message.chat.id
            # Проверка, что пользователь является организатором
            event = self.event_service.get_event(event_id)
            if event and event.host_id == user_id:
                self.event_service.delete_event(event_id)
                self.bot.send_message(call.message.chat.id, f"Мероприятие '{event.name}' было отменено.")
            else:
                self.bot.send_message(call.message.chat.id, "Вы не можете отменить это мероприятие.")

        self.bot.polling(none_stop=True)

    def create_event_name(self, message):
        name = message.text
        self.bot.send_message(message.chat.id, "Введите описание мероприятия:")
        self.bot.register_next_step_handler(message, self.create_event_description, name)

    def create_event_description(self, message, name):
        description = message.text
        self.bot.send_message(message.chat.id, "Введите место проведения мероприятия:")
        self.bot.register_next_step_handler(message, self.create_event_place, name, description)

    def create_event_place(self, message, name, description):
        place = message.text
        self.bot.send_message(message.chat.id, "Введите дату и время мероприятия (формат: ГГГГ-ММ-ДД ЧЧ:ММ):")
        self.bot.register_next_step_handler(message, self.create_event_date_time, name, description, place)

    def create_event_date_time(self, message, name, description, place):
        date_time = message.text
        self.bot.send_message(message.chat.id, "Введите лимит участников (оставьте пустым, если лимит не установлен):")
        self.bot.register_next_step_handler(message, self.create_event_participant_limit, name, description, place,
                                            date_time)

    def create_event_participant_limit(self, message, name, description, place, date_time):
        limit = message.text
        if limit.isdigit():
            participant_limit = int(limit)
        else:
            participant_limit = None
        self.bot.send_message(message.chat.id, "Введите название организации, организующей мероприятие:")
        self.bot.register_next_step_handler(message, self.create_event_host_name, name, description, place, date_time,
                                            participant_limit)

    def create_event_host_name(self, message, name, description, place, date_time, participant_limit):
        host_name = message.text
        user_id = message.chat.id
        try:
            event_id = self.event_service.create_event(user_id, name, description, place, date_time, participant_limit,
                                                       host_name)
            self.bot.send_message(message.chat.id, f"Мероприятие '{name}' успешно создано!")
        except PermissionError:
            self.bot.send_message(message.chat.id,
                                  "Вы не можете создать больше двух мероприятия. Подтвердите свой номер телефона с помощью команды /verify.")

