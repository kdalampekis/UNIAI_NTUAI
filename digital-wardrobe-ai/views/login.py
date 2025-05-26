

DB_PATH = 'data/wardrobe.db'
import streamlit as st
import sqlite3
import bcrypt

def verify_user(username: str, password: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()

    if result:
        user_id, password_hash = result
        if bcrypt.checkpw(password.encode(), password_hash.encode()):
            return user_id
    return None

def render():
    st.title("👤 Login to Your Wardrobe")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not username or not password:
            st.warning("Please enter both username and password.")
            return

        user_id = verify_user(username, password)
        if user_id:
            # ← Change this to match your sidebar label exactly
            st.session_state.user_id = user_id
            st.session_state.page = "My Closet"
            st.success("Login successful! Redirecting...")
            st.rerun()
        else:
            st.error("Invalid username or password")
