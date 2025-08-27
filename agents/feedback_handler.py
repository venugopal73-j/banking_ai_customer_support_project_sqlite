from agents.ticket_manager import TicketManager

class FeedbackHandlerAgent:
    def __init__(self):
        self.ticket_manager = TicketManager()

    def handle_feedback(self, message, category):
        if category == "positive":
            return "✅ We're so glad you're happy! Thanks for your kind words—we're thrilled to know we could make your experience a positive one!"
        else:
            ticket_id = self.ticket_manager.create_ticket(message, category)
            return f"📩 Thank you for taking the time to share this. We've made sure it's been passed directly to our team.. Ticket ID: `{ticket_id}` ✅"

    def get_ticket_history(self):
        return self.ticket_manager.get_ticket_history()
