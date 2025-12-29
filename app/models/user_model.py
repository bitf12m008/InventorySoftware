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
            SELECT user_id, username, role, status
            FROM Users
            WHERE username = ?
              AND password_hash = ?
              AND status = 'active'
        """, (username, password_hash))

        row = cur.fetchone()
        conn.close()

        if not row:
            return None

        return {
            "user_id": row["user_id"],
            "username": row["username"],
            "role": row["role"],
            "status": row["status"]
        }

    @staticmethod
    def create(username, password_hash, role):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO Users (username, password_hash, role, status)
            VALUES (?, ?, ?, 'active')
        """, (username, password_hash, role))

        conn.commit()
        conn.close()

    @staticmethod
    def exists(username):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute(
            "SELECT 1 FROM Users WHERE username = ?",
            (username,)
        )
        exists = cur.fetchone() is not None

        conn.close()
        return exists

    @staticmethod
    def get_all_staff():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
            SELECT user_id, username, role, status
            FROM Users
            WHERE role = 'staff'
            ORDER BY username
        """)

        rows = cur.fetchall()
        conn.close()

        return [
            {
                "id": r["user_id"],
                "username": r["username"],
                "role": r["role"],
                "status": r["status"]
            }
            for r in rows
        ]

    @staticmethod
    def deactivate_user(user_id):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
            UPDATE Users
            SET status = 'inactive'
            WHERE user_id = ?
        """, (user_id,))

        conn.commit()
        conn.close()

    @staticmethod
    def update_password(user_id, password_hash):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
            UPDATE Users
            SET password_hash = ?
            WHERE user_id = ?
        """, (password_hash, user_id))

        conn.commit()
        conn.close()
