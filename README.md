# 🏦 Banking Customer Support AI Agent (Multi-Agent System)

This project is a capstone implementation of a **Generative AI-based multi-agent architecture** to simulate intelligent customer support for a banking use case.

---

## 📌 Features

- 🤖 Classifies customer messages as Feedback (Positive/Negative) or Ticket Queries
- 🙏 Routes feedback to a response agent with empathy
- 🗃️ Stores and tracks complaint tickets using **SQLite**
- 🔍 Handles ticket status inquiries
- 🖥️ Clean Streamlit-based UI
- ✅ Modular, testable, and free-tier compliant

---

## 🗂️ Project Structure

```
project-root/
├── app.py
├── requirements.txt
├── agents/
│   ├── __init__.py
│   ├── classifier_agent.py
│   ├── feedback_handler.py
│   └── query_handler.py
├── tests/
│   ├── test_classifier_agent.py
│   ├── test_feedback_handler.py
│   └── test_query_handler.py
├── data/
│   └── support_tickets.db (auto-created)
```

---

## 🛠️ Installation

```bash
git clone <repo-url>
cd project-root
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

## 🚀 Run the App

```bash
streamlit run app.py
```

---

## 🧪 Run Unit Tests

```bash
python -m unittest discover tests
```

---

## ☁️ Deploy to Streamlit Cloud

1. Push code to a public GitHub repo
2. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Set `app.py` as the entry point
4. Add this pre-run command in the setup:
   ```bash
   python -m spacy download en_core_web_sm
   ```

---

## 📦 Tech Stack

- **LLMs**: Hugging Face Transformers (Free-tier)
- **NLP**: spaCy, VADER
- **DB**: SQLite (file-based)
- **UI**: Streamlit
- **Tests**: unittest

---

## 👨‍🔬 Author Note

Designed for modularity, readability, and ease of deployment. Built for educational, demo, or light production use cases.