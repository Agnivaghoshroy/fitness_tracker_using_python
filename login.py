# app.py
import streamlit as st
import sqlite3
import hashlib

# Database setup
def create_connection():
    conn = sqlite3.connect('fitness_tracker.db', check_same_thread=False)
    return conn

def create_users_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User registration
def register_user(conn, username, password):
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    try:
        cursor.execute('''
            INSERT INTO users (username, password)
            VALUES (?, ?)
        ''', (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists

# User login
def login_user(conn, username, password):
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    cursor.execute('''
        SELECT * FROM users
        WHERE username = ? AND password = ?
    ''', (username, hashed_password))
    user = cursor.fetchone()
    return user is not None

# Login page
def login_page():
    st.title("Personal Fitness Tracker")
    st.sidebar.title("Account")
    choice = st.sidebar.radio("Choose an option", ["Login", "Register"])

    conn = create_connection()
    create_users_table(conn)

    if choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(conn, username, password):
                st.success("Logged in as {}".format(username))
                # Update session state and redirect to main app
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()  # Refresh the page to load the main app
            else:
                st.error("Invalid username or password. Please register if user is not registered.")

    elif choice == "Register":
        st.subheader("Create a new account")
        new_username = st.text_input("Choose a username")
        new_password = st.text_input("Choose a password", type="password")
        confirm_password = st.text_input("Confirm password", type="password")

        if st.button("Register"):
            if new_password == confirm_password:
                if register_user(conn, new_username, new_password):
                    st.success("Account created successfully! Please log in.")
                else:
                    st.error("Username already exists. Please choose another.")
            else:
                st.error("Passwords do not match. Please try again.")

    # Close the database connection
    conn.close()

# Main function to handle routing
def main():
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""

    # Redirect based on login status
    if st.session_state.logged_in:
        from main_app import main_app  # Dynamically import the main app
        main_app()  # Show the main app if logged in
    else:
        login_page()  # Show the login page if not logged in

if __name__ == "__main__":
    main()