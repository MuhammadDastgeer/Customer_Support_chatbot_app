# backend/chat_engine.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "customer_support.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # users table (for simple login)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE
    )
    """)
    # messages table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        message TEXT,
        role TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

# ensure DB/tables exist on import
init_db()

# --- user helpers ---
def add_user(username: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (username,))
    conn.commit()
    conn.close()

def get_user_id(username: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

# --- message helpers ---
def save_message(user_id: str, message: str, role: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (user_id, message, role) VALUES (?, ?, ?)",
        (user_id, message, role)
    )
    conn.commit()
    conn.close()

def load_history(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, created_at, message, role FROM messages WHERE user_id = ? ORDER BY id ASC", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

# --- FAQ + restricted customer support replies only ---
_FAQS = {
    "refund policy": "Our refund policy allows returns within 30 days of purchase.",
    "delivery time": "Delivery usually takes 3-5 business days.",
    "support email": "You can reach us at support@company.com",
    "working hours": "Our support team is available Mon-Fri, 9am-6pm.",
    "shipping": "We ship domestically within 3-5 business days (international shipping available on select items).",
    "cancel order": "You can cancel orders within 1 hour of placement from your account page if not processed yet."
}

def _check_faqs(text: str):
    t = text.lower()
    for key, ans in _FAQS.items():
        if key in t:
            return ans
    return None

def get_response(user_id: str, user_query: str) -> str:
    """
    Return a customer-support-only reply.
    - If the query matches known FAQ keywords, return the FAQ answer.
    - Otherwise return a polite fallback saying only customer-support queries are handled.
    """
    if not user_query or not user_query.strip():
        return "Please enter your question."

    # FAQ match
    faq_ans = _check_faqs(user_query)
    if faq_ans:
        return faq_ans

    # If not matching known FAQs, keep response within customer-support domain.
    # You can expand this block to add more rule-based replies.
    allowed_keywords = ["order", "refund", "return", "shipping", "delivery", "cancel", "account", "payment", "support", "email"]
    lowered = user_query.lower()
    if any(k in lowered for k in allowed_keywords):
        # simple templated reply (you can later plug LLM here)
        return "I can help with orders, refunds, shipping, cancellations and account issues. Please give more details about your order or issue."
    else:
        return "I can only help with customer support related queries (orders, refunds, shipping, accounts)."

