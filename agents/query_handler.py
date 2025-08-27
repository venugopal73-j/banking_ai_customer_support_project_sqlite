from agents.ticket_manager import TicketManager

class QueryHandlerAgent:
    def __init__(self):
        self.ticket_manager = TicketManager()

    def handle_query(self, message):
        ticket_id = self.ticket_manager.create_ticket(message, category="query")
        return f"📩 Your query has been received and logged. Ticket ID: `{ticket_id}` ✅"

    def get_ticket_history(self):
        return self.ticket_manager.get_ticket_history()
