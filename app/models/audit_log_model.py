from datetime import datetime
import sqlite3
from app.db.database_init import get_connection


class AuditLogModel:
    @staticmethod
    def log(
        action,
        entity_type,
        entity_id=None,
        shop_id=None,
        product_id=None,
        user_id=None,
        username=None,
        details=None,
    ):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO AuditLogs
            (user_id, username, action, entity_type, entity_id, shop_id, product_id, details, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                username,
                action,
                entity_type,
                entity_id,
                shop_id,
                product_id,
                details,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def create_with_cursor(
        cursor,
        action,
        entity_type,
        entity_id=None,
        shop_id=None,
        product_id=None,
        user_id=None,
        username=None,
        details=None,
    ):
        cursor.execute(
            """
            INSERT INTO AuditLogs
            (user_id, username, action, entity_type, entity_id, shop_id, product_id, details, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                username,
                action,
                entity_type,
                entity_id,
                shop_id,
                product_id,
                details,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )

    @staticmethod
    def get_logs(limit=500, username=None, action=None, query=None):
        conn = get_connection(sqlite3.Row)
        cur = conn.cursor()

        sql = """
            SELECT
                audit_id,
                user_id,
                username,
                action,
                entity_type,
                entity_id,
                shop_id,
                product_id,
                details,
                created_at
            FROM AuditLogs
            WHERE 1=1
        """
        params = []

        if username:
            sql += " AND username = ?"
            params.append(username)

        if action:
            sql += " AND action = ?"
            params.append(action)

        if query:
            sql += " AND (details LIKE ? OR entity_type LIKE ? OR action LIKE ?)"
            like = f"%{query}%"
            params.extend([like, like, like])

        sql += " ORDER BY audit_id DESC LIMIT ?"
        params.append(limit)

        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.close()
        return rows
