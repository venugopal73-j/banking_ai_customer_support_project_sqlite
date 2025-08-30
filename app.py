import streamlit as st
import shutil
import sqlite3
import os
import logging
from agents.classifier_agent import ClassifierAgent
from agents.feedback_handler import FeedbackHandlerAgent
from agents.query_handler import QueryHandlerAgent
import pandas as pd
from dotenv import load_dotenv
from agents.ticket_manager import initialize_database

# Load environment variables
load_dotenv()

# --- STEP 1: Backup before schema check ---
db_path = "tickets.db"
backup_path = "tickets_backup.db"

print("tickets.db exists:", os.path.exists(db_path))
print("tickets_backup.db exists:", os.path.exists(backup_path))

if os.path.exists(db_path) and not os.path.exists(backup_path):
    shutil.copy(db_path, backup_path)
    print("✅ Forced backup created manually.")
else:
    print("⚠️ Backup skipped (already exists or DB missing)")

# --- STEP 2: Validate schema (will raise if 'id' column is missing) ---
initialize_database()  # Only validates, does not delete or reset DB

# --- STEP 3: Logging setup ---
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# --- STEP 4: Agent setup ---
classifier = ClassifierAgent()
feedback_handler = FeedbackHandlerAgent()
query_handler = QueryHandlerAgent()

# --- STEP 5: Streamlit UI ---
st.set_page_config(page_title="AI Customer Support Agent", layout="wide")
st.title("🤖 AI-Powered Banking Customer Support Agent")
st.markdown("Enter your message and let the AI classify, respond, and manage tickets!")

user_message = st.text_area("💬 Type your message here")

if st.button("Submit"):
    if user_message.strip() == "":
        st.warning("Please enter a message.")
    else:
        logging.info(f"User message: {user_message}")
        category = classifier.classify(user_message)
        logging.info(f"Classified as: {category}")
        st.markdown(f"**🔍 Message classified as:** `{category}`")

        if category in ["positive", "negative"]:
            response = feedback_handler.handle_feedback(user_message, category)
            st.success(response)
            logging.info(f"Feedback Handler Response: {response}")

        elif category == "query":
            response = query_handler.handle_query(user_message)
            st.info(response)
            logging.info(f"Query Handler Response: {response}")
        else:
            st.error("❗ Unable to classify message. Please try again.")

# --- Ticket History Section ---
st.markdown("---")
if st.checkbox("Show Ticket History (from DB)"):
    try:
        history = query_handler.get_ticket_history()
        if not history:
            st.info("No tickets found.")
        else:
            df = pd.DataFrame(history)

            expected_columns = ['ticket_id', 'message', 'category', 'status', 'created_at']
            for col in expected_columns:
                if col not in df.columns:
                    df[col] = "N/A"

            df = df[expected_columns]
            df = df.sort_values(by='ticket_id', ascending=False)
            st.dataframe(df)
    except Exception as e:
        st.error(f"Error fetching ticket history: {e}")

# --- Enquiry Section ---
st.subheader("🔎 Enquire About a Ticket")
ticket_input = st.text_input("Enter your Ticket ID (e.g., 100007):")

if st.button("Check Ticket Status"):
    if not ticket_input.strip().isdigit():
        st.warning("Please enter a valid numeric Ticket ID.")
    else:
        ticket_id = int(ticket_input.strip())
        ticket_info = query_handler.ticket_manager.get_ticket_by_customer_id(ticket_id)

        if ticket_info:
            st.markdown(f"**📝 Message:** {ticket_info['message']}")
            st.markdown(f"**📅 Created At:** {ticket_info['created_at']}")
            st.markdown(f"**📌 Status:** {ticket_info['status']}")
        else:
            st.error("❗ Ticket not found. Please check the ID and try again.")
