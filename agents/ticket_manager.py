# agents/ticket_manager.py

from datetime import datetime
from sqlite_utils import Database
import os

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

    def get_ticket_history(self):
        rows = list(self.table.rows)
        sorted_rows = sorted(rows, key=lambda x: x.get("id", 0), reverse=True)

        for row in sorted_rows:
            row["ticket_id"] = 100000 + row["id"]
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