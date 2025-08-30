import streamlit as st
import shutil
import sqlite3
import os
import logging
from dotenv import load_dotenv
import pandas as pd

from agents.classifier_agent import ClassifierAgent
from agents.feedback_handler import FeedbackHandlerAgent
from agents.query_handler import QueryHandlerAgent
from agents.ticket_manager import initialize_database

# Load environment variables
load_dotenv()

# --- STEP 1: Backup tickets.db if not already backed up ---
db_path = "tickets.db"
backup_path = "tickets_backup.db"

print("tickets.db exists:", os.path.exists(db_path))
print("tickets_backup.db exists:", os.path.exists(backup_path))

if os.path.exists(db_path) and not os.path.exists(backup_path):
    shutil.copy(db_path, backup_path)
    print("✅ Forced backup created manually.")
else:
    print("⚠️ Backup skipped (already exists or DB missing)")

# --- STEP 2: Schema migration if needed ---
def migrate_schema_if_needed(db_path="tickets.db"):
    if not os.path.exists(db_path):
        print("No existing DB found; skipping migration.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if 'tickets' table exists at all
    cursor.execute("""
        SELECT name FROM sqlite_master WHERE type='table' AND name='tickets';
    """)
    table_exists = cursor.fetchone()

    if not table_exists:
        print("🆕 'tickets' table not found. Creating new table with schema...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)
        conn.commit()
        print("✅ Created new 'tickets' table.")
        conn.close()
        return

    # Check if 'id' column exists in the table
    cursor.execute("PRAGMA table_info(tickets);")
    columns = [col[1] for col in cursor.fetchall()]

    if "id" not in columns:
        print("🔁 Migrating: Adding 'id' column to existing tickets table...")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets_temp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)

        cursor.execute("""
            INSERT INTO tickets_temp (message, category, status, created_at)
            SELECT message, category, status, created_at FROM tickets;
        """)

        cursor.execute("DROP TABLE tickets;")
        cursor.execute("ALTER TABLE tickets_temp RENAME TO tickets;")
        conn.commit()
        print("✅ Migration complete: 'id' column added.")
    else:
        print("✅ Schema OK: 'id' column already exists.")
    conn.close()

# --- STEP 3: Migrate Schema Then Initialize ---
migrate_schema_if_needed()
initialize_database()

# --- STEP 4: Logging Setup ---
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# --- STEP 5: Initialize AI Agents ---
classifier = ClassifierAgent()
feedback_handler = FeedbackHandlerAgent()
query_handler = QueryHandlerAgent()

# --- STEP 6: Streamlit UI ---
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

# --- STEP 7: Ticket History Display ---
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

# --- STEP 8: Check Ticket Status ---
st.subheader("🔎 Enquire About a Ticket")
ticket_input = st.text_input("Enter your Ticket ID (e.g., 100007):")

if st.button("Check Ticket Status"):
    if not ticket_input.strip().isdigit():
        st.warning("Please enter a valid numeric Ticket ID.")
    else:
        ticket_id = int(ticket_input.strip())
        try:
            ticket_info = query_handler.ticket_manager.get_ticket_by_customer_id(ticket_id)
            if ticket_info:
                st.markdown(f"**📝 Message:** {ticket_info['message']}")
                st.markdown(f"**📅 Created At:** {ticket_info['created_at']}")
                st.markdown(f"**📌 Status:** {ticket_info['status']}")
            else:
                st.error("❗ Ticket not found. Please check the ID and try again.")
        except Exception as e:
            st.error(f"Error retrieving ticket: {e}")
