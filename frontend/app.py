# frontend/app.py
import streamlit as st
import sys, os

# Make sure parent directory (project root) is in path so "backend" package is found.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend import chat_engine

# -------------------------
# Session state initialization
# -------------------------
if "page" not in st.session_state:
    st.session_state.page = "login"
if "username" not in st.session_state:
    st.session_state.username = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# -------------------------
# Login page
# -------------------------
def login_page():
    st.title("🔐 Customer Support - Login")
    st.markdown("Enter a username to login (no password required for this demo).")

    username = st.text_input("Username")
    if st.button("Login"):
        if username and username.strip():
            username = username.strip()
            # ensure user in DB
            chat_engine.add_user(username)
            uid = chat_engine.get_user_id(username)
            st.session_state.username = username
            st.session_state.user_id = str(uid)
            st.session_state.page = "welcome"
            st.success(f"Logged in as {username}")
            st.rerun()
        else:
            st.error("Enter a valid username.")

# -------------------------
# Welcome page
# -------------------------
def welcome_page():
    st.title("🎉 Welcome")
    st.markdown(f"### 👋 Hello, **{st.session_state.username}**")
    st.write("Click below to go to your chat.")

    col1, col2 = st.columns([3,1])
    with col1:
        if st.button("👉 Go to Chat"):
            st.session_state.page = "chat"
            st.rerun()
    with col2:
        if st.button("🚪 Logout"):
            # clear session
            st.session_state.page = "login"
            st.session_state.username = None
            st.session_state.user_id = None
            st.rerun()

# -------------------------
# Chat page
# -------------------------
def chat_page():
    st.title("💬 Customer Support Chat")
    # Top row: welcome + logout
    col1, col2 = st.columns([5,1])
    with col1:
        st.markdown(f"**Welcome, {st.session_state.username}**")
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.page = "login"
            st.session_state.username = None
            st.session_state.user_id = None
            st.rerun()

    st.divider()

    # Load and show history
    history = chat_engine.load_history(st.session_state.user_id)
    if history:
        for row in history:
            # row: (id, created_at, message, role)
            _, created_at, message, role = row
            if role == "user":
                st.chat_message("user").write(message)
            else:
                st.chat_message("assistant").write(message)
    else:
        st.info("No conversation history yet. Ask a question below.")

    # Chat input
    user_input = st.chat_input("Type your message...")
    if user_input:
        # Save user message
        chat_engine.save_message(st.session_state.user_id, user_input, "user")
        st.chat_message("user").write(user_input)

        # Get response (backend)
        response = chat_engine.get_response(st.session_state.user_id, user_input)

        # Save and show assistant reply
        chat_engine.save_message(st.session_state.user_id, response, "assistant")
        st.chat_message("assistant").write(response)
        # rerun to reflect saved history (optional)
        st.rerun()

# -------------------------
# Router
# -------------------------
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "welcome":
    if not st.session_state.username:
        st.session_state.page = "login"
        st.rerun()
    welcome_page()
elif st.session_state.page == "chat":
    if not st.session_state.username:
        st.session_state.page = "login"
        st.rerun()
    chat_page()
