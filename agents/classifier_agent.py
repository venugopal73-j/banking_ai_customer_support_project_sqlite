import os
import requests
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

class ClassifierAgent:
    def __init__(self):
        # First try from Streamlit secrets, then fallback to env variable
        api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY not found in Streamlit secrets or .env file.")
        self.api_key = api_key
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama3-70b-8192"

    def classify(self, message: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        prompt = (
            "Classify the following user message into one of three categories: "
            "'positive', 'negative', or 'query'. "
            "Respond with only one word (positive, negative, or query).\n\n"
            f"User message: {message}"
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a classification assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        response = requests.post(self.api_url, headers=headers, json=payload)
        response.raise_for_status()

        try:
            result = response.json()
            reply = result["choices"][0]["message"]["content"].strip().lower()
            if reply in ["positive", "negative", "query"]:
                return reply
        except Exception as e:
            print("Classification error:", e)

        return "unknown"
