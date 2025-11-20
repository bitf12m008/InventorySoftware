import hashlib
import sqlite3
import os
import sys

def get_base_path():
    if hasattr(sys, "_MEIPASS"):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = get_base_path()
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "app.db")

class AuthService:

    @staticmethod
    def hash_password(password: str):
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def login(username: str, password: str):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT user_id, username, password_hash, role FROM Users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return None  # username not found

        user_id, username, password_hash, role = user

        if password_hash == AuthService.hash_password(password):
            return {
                "user_id": user_id,
                "username": username,
                "role": role
            }
        else:
            return None
