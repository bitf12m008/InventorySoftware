import sqlite3
import hashlib
import secrets
import hmac
from app.db.database_init import get_connection

PBKDF2_ALGO = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 200_000
STAFF_PERMISSION_KEYS = (
    "add_sale",
    "add_purchase",
    "show_sales",
    "view_profit_report",
    "view_weekly_profit",
)
DEFAULT_STAFF_PERMISSIONS = ("add_sale", "show_sales")

class UserModel:
    STAFF_PERMISSION_KEYS = STAFF_PERMISSION_KEYS
    DEFAULT_STAFF_PERMISSIONS = DEFAULT_STAFF_PERMISSIONS

    @staticmethod
    def hash_password(password: str) -> str:
        salt = secrets.token_hex(16)
        dk = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            PBKDF2_ITERATIONS
        )
        return f"{PBKDF2_ALGO}${PBKDF2_ITERATIONS}${salt}${dk.hex()}"

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        if not stored_hash:
            return False

        if stored_hash.startswith(f"{PBKDF2_ALGO}$"):
            try:
                _, iterations, salt, digest = stored_hash.split("$", 3)
                derived = hashlib.pbkdf2_hmac(
                    "sha256",
                    password.encode("utf-8"),
                    salt.encode("utf-8"),
                    int(iterations)
                ).hex()
                return hmac.compare_digest(derived, digest)
            except (TypeError, ValueError):
                return False

        legacy_hash = hashlib.sha256(password.encode()).hexdigest()
        return hmac.compare_digest(legacy_hash, stored_hash)

    @staticmethod
    def authenticate(username: str, password: str):
        if not username or not password:
            return None

        conn = get_connection(sqlite3.Row)
        cur = conn.cursor()

        cur.execute("""
            SELECT user_id, username, role, status, password_hash
            FROM Users
            WHERE username = ?
              AND status = 'active'
        """, (username,))

        row = cur.fetchone()
        if not row or not UserModel.verify_password(password, row["password_hash"]):
            conn.close()
            return None

        if not row["password_hash"].startswith(f"{PBKDF2_ALGO}$"):
            upgraded_hash = UserModel.hash_password(password)
            cur.execute(
                "UPDATE Users SET password_hash = ? WHERE user_id = ?",
                (upgraded_hash, row["user_id"])
            )
            conn.commit()

        conn.close()

        result = {
            "user_id": row["user_id"],
            "username": row["username"],
            "role": row["role"],
            "status": row["status"]
        }
        if row["role"] == "staff":
            result["permissions"] = UserModel.get_permissions(row["user_id"])
        return result

    @staticmethod
    def create(username, password_hash, role):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO Users (username, password_hash, role, status)
            VALUES (?, ?, ?, 'active')
        """, (username, password_hash, role))

        user_id = cur.lastrowid
        conn.commit()
        conn.close()
        return user_id

    @staticmethod
    def exists(username):
        conn = get_connection()
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
        conn = get_connection(sqlite3.Row)
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
        conn = get_connection()
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
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE Users
            SET password_hash = ?
            WHERE user_id = ?
        """, (password_hash, user_id))

        conn.commit()
        conn.close()

    @staticmethod
    def get_by_id(user_id):
        conn = get_connection(sqlite3.Row)
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id, username, role, status FROM Users WHERE user_id = ?",
            (user_id,)
        )
        row = cur.fetchone()
        conn.close()
        return row

    @staticmethod
    def get_permissions(user_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT permission_key
            FROM StaffPermissions
            WHERE user_id = ?
            ORDER BY permission_key
            """,
            (user_id,)
        )
        rows = [r[0] for r in cur.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def set_permissions(user_id, permissions):
        valid = sorted(set(
            p for p in permissions
            if p in STAFF_PERMISSION_KEYS
        ))
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM StaffPermissions WHERE user_id = ?",
            (user_id,)
        )
        if valid:
            cur.executemany(
                """
                INSERT INTO StaffPermissions (user_id, permission_key)
                VALUES (?, ?)
                """,
                [(user_id, p) for p in valid]
            )
        conn.commit()
        conn.close()
        return valid
