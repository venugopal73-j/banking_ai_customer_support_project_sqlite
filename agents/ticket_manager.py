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
      if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
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

    def get_ticket_history(self):
        rows = list(self.table.rows)
        
        # Safely sort by 'id'
        sorted_rows = sorted(rows, key=lambda x: x.get("id", 0), reverse=True)

        # Add 'ticket_id' field for display purposes
        for row in sorted_rows:
            if "id" in row:
                row["ticket_id"] = 100000 + row["id"]
            else:
                row["ticket_id"] = "UNKNOWN"

        return sorted_rows
    def get_ticket_by_customer_id(self, customer_ticket_id):
        actual_id = customer_ticket_id - 100000
        try:
            row = self.table.get(actual_id)
            return {
                "ticket_id": customer_ticket_id,
                "message": row["message"],
                "created_at": row["created_at"],
                "status": row["status"]
            }
        except Exception as e:
            return None