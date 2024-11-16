# adapters/db/sqlite_event_repository.py

import sqlite3
from v2.project.domain.entities.event import Event
from v2.project.domain.ports.event_repository import EventRepository

class SQLiteEventRepository(EventRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def add_event(self, event: Event) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO events (name, description, place, date_time, participant_limit, host_id, host_name, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (event.name, event.description, event.place, event.date_time, event.participant_limit, event.host_id, event.host_name, event.status)
        )
        conn.commit()
        event_id = cursor.lastrowid
        conn.close()
        return event_id

    def get_event(self, event_id: int) -> Event:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Event(*row)
        return None

    def get_upcoming_events(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE date_time > datetime('now')")
        rows = cursor.fetchall()
        conn.close()
        return [Event(*row) for row in rows]

    def delete_event(self, event_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
        conn.commit()
        conn.close()

    def update_event(self, event: Event):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE events SET name = ?, description = ?, place = ?, date_time = ?, participant_limit = ?, host_id = ?, host_name = ?, participant_count = ?, status = ? WHERE id = ?",
            (event.name, event.description, event.place, event.date_time, event.participant_limit, event.host_id, event.host_name, event.participant_count, event.status, event.id)
        )
        conn.commit()
        conn.close()

    def get_user_events(self, user_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM events WHERE host_id = ? and date_time > datetime('now')", (user_id,)
        )
        rows = cursor.fetchall()
        conn.commit()
        conn.close()
        return [Event(*row) for row in rows]

    def register_user_for_event(self, user_id: int, event_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO registrations (user_id, event_id) VALUES (?, ?)",
                       (user_id, event_id))
        conn.commit()
        conn.close()

    def get_event_participants(self, event_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM registrations WHERE event_id = ?", (event_id,))
        users_id = cursor.fetchall()
        conn.close()
        return users_id
