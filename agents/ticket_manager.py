# agents/ticket_manager.py

from datetime import datetime
from sqlite_utils import Database
import os
import sqlite3


class TicketManager:
    def __init__(self, db_path="tickets.db"):
        self.db = Database(db_path)
        self.table = self.db["tickets"]

    def create_ticket(self, message, category):
        created_at = datetime.utcnow().isoformat()
        status = "open"

        inserted = self.table.insert({
            "message": message,
            "category": category,
            "created_at": created_at,
            "status": status
        }, alter=True)

        ticket_row = self.table.last_pk
        return 100000 + ticket_row if ticket_row else "UNKNOWN"
def initialize_database(db_path="tickets.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ensure 'id' column exists by checking schema
    cursor.execute("PRAGMA table_info(tickets)")
    columns = [col[1] for col in cursor.fetchall()]

    if "id" not in columns:
        raise RuntimeError("Existing 'tickets' table is missing 'id' column. Manual migration required.")

    # If table doesn't exist, create it
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            category TEXT,
            created_at TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()


class TicketManager:
    def __init__(self, db_path="tickets.db"):
        self.db = Database(db_path)
        self.table = self.db["tickets"]
        self.db_path = db_path

    def create_ticket(self, message, category):
        created_at = datetime.utcnow().isoformat()
        status = "open"

        inserted = self.table.insert({
            "message": message,
            "category": category,
            "created_at": created_at,
            "status": status
        }, alter=True)

        ticket_row = self.table.last_pk
        return 100000 + ticket_row if ticket_row else "UNKNOWN"

    def get_ticket_history(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets")
        rows = cursor.fetchall()
        result = []
        for row in rows:
            ticket_id = 100000 + int(row[0]) if row[0] is not None else "UNKNOWN"
            result.append({
                "ticket_id": ticket_id,
                "message": row[1],
                "category": row[2],
                "created_at": row[3],
                "status": row[4]
            })
        conn.close()
        return result

    def get_ticket_by_customer_id(self, ticket_id):
        internal_id = ticket_id - 100000
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets WHERE id=?", (internal_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "ticket_id": ticket_id,
                "message": row[1],
                "category": row[2],
                "created_at": row[3],
                "status": row[4]
            }
        return None