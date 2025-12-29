import sqlite3
import hashlib
from app.db.database_init import DB_PATH

class UserModel:

    @staticmethod
    def authenticate(username: str, password: str):
        if not username or not password:
            return None

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
            SELECT user_id, username, role
            FROM Users
            WHERE username = ? AND password_hash = ?
        """, (username, password_hash))

        row = cur.fetchone()
        conn.close()

        if not row:
            return None

        return {
            "user_id": row["user_id"],
            "username": row["username"],
            "role": row["role"]
        }
    
    @staticmethod
    def create(username, password_hash, role):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO Users (username, password_hash, role)
            VALUES (?, ?, ?)
        """, (username, password_hash, role))

        conn.commit()
        conn.close()

    @staticmethod
    def exists(username):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute(
            "SELECT 1 FROM Users WHERE username=?",
            (username,)
        )
        exists = cur.fetchone() is not None

        conn.close()
        return exists
