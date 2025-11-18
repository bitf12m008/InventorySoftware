import hashlib
import sqlite3

DB_PATH = "database/app.db"

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
