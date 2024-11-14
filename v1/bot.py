import telebot
import sqlite3
from telebot import types


TOKEN = '7473067108:AAERYtQit6t6Yu4pfTBdVMp3CNSSDIN9PhU'
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'main', 'menu'])
def hello(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Создание мероприятия', callback_data='creating', callback_query=message)
    btn2 = types.InlineKeyboardButton('Список мероприятий', callback_data='list_events', callback_message=message)
    markup.add(btn1)
    markup.add(btn2)

    bot.send_message(message.chat.id,
                     f'Привет, {message.from_user.first_name}, я оффник. Готов помочь тебе в любую секунду!',
                     reply_markup=markup)


def init_db():
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        date TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS registrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        event_id INTEGER NOT NULL,
                        FOREIGN KEY (event_id) REFERENCES events(id))''')
    conn.commit()
    conn.close()


init_db()


@bot.message_handler(commands=['create_event'])
def create_event(message):
    if message.chat.type == "private":
        bot.send_message(message.chat.id, "Введите название мероприятия:")
        bot.register_next_step_handler(message, process_event_name)


def process_event_name(message):
    event_name = message.text
    bot.send_message(message.chat.id, "Введите описание мероприятия:")
    bot.register_next_step_handler(message, process_event_description, event_name)


def process_event_description(message, event_name):
    event_description = message.text
    bot.send_message(message.chat.id, "Введите дату мероприятия (в формате ДД-ММ-ГГГГ):")
    bot.register_next_step_handler(message, process_event_date, event_name, event_description)


def process_event_date(message, event_name, event_description):
    event_date = message.text
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO events (name, description, date) VALUES (?, ?, ?)",
                   (event_name, event_description, event_date))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, "Мероприятие успешно создано!")


@bot.message_handler(commands=['list_events'])
def list_events(message):
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, date, description FROM events")
    events = cursor.fetchall()
    conn.close()

    if not events:
        bot.send_message(message.chat.id, "Нет доступных мероприятий.")
    else:
        for event in events:
            event_id, event_name, event_date, event_description = event
            markup = types.InlineKeyboardMarkup()
            register_button = types.InlineKeyboardButton(text="Регистрация", callback_data=f"registration_{event_id}")
            markup.add(register_button)
            bot.send_message(message.chat.id, f"📅 *{event_name}*\nДата: {event_date}\nОписание: {event_description}", parse_mode="Markdown",
                             reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_message(call):
    if call.data == 'creating':
        bot.send_message(call.message.chat.id, "Введите название мероприятия:")
        bot.register_next_step_handler(call.message, process_event_name)

    elif call.data == 'list_events':
        list_events(call.message)

    elif call.data.startswith('registration_'):
        event_id = int(call.data.split("_")[1])
        user_id = call.from_user.id

        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registrations WHERE user_id = ? AND event_id = ?", (user_id, event_id))
        registration = cursor.fetchone()

        if registration:
            bot.answer_callback_query(call.id, "Вы уже зарегистрированы на это мероприятие.")
        else:
            cursor.execute("INSERT INTO registrations (user_id, event_id) VALUES (?, ?)", (user_id, event_id))
            conn.commit()
            bot.answer_callback_query(call.id, "Вы успешно зарегистрировались на мероприятие!")

        conn.close()


@bot.message_handler(commands=['my_registrations'])
def my_registrations(message):
    user_id = message.from_user.id
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT events.name, events.date FROM events 
                      JOIN registrations ON events.id = registrations.event_id 
                      WHERE registrations.user_id = ?""", (user_id,))
    registrations = cursor.fetchall()
    conn.close()

    if not registrations:
        bot.send_message(message.chat.id, "Вы еще не зарегистрированы на мероприятия.")
    else:
        response = "Ваши регистрации:\n\n"
        for event_name, event_date in registrations:
            response += f"📅 {event_name} — {event_date}\n"
        bot.send_message(message.chat.id, response)


bot.polling(none_stop=True)
