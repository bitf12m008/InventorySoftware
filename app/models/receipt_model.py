from datetime import datetime
from app.db.database_init import get_connection


class ReceiptModel:
    @staticmethod
    def create(sale_id, file_path):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO Receipts (sale_id, file_path, date)
            VALUES (?, ?, ?)
            """,
            (sale_id, file_path, datetime.now().isoformat(timespec="seconds")),
        )
        receipt_id = cur.lastrowid
        conn.commit()
        conn.close()
        return receipt_id
