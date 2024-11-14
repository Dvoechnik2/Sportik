# adapters/db/sqlite_user_repository.py

import sqlite3
from v2.project.domain.entities.user import User
from v2.project.domain.ports.user_repository import UserRepository

class SQLiteUserRepository(UserRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_user(self, user_id: int) -> User:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, name, phone FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(row[0], row[1], row[2])
        return None

    def add_user(self, user: User):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id, name, phone) VALUES (?, ?, ?)", (user.user_id, user.name, user.phone))
        conn.commit()
        conn.close()

    def verify_user_phone(self, user_id: int, phone: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET phone = ? WHERE user_id = ?", (phone, user_id))
        conn.commit()
        conn.close()

    def register_user_for_event(self, user_id: int, event_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO registrations (user_id, event_id) VALUES (?, ?)",
                       (user_id, event_id))
        conn.commit()
        conn.close()