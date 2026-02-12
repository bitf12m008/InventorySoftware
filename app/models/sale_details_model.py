import sqlite3
from datetime import datetime
from app.db.database_init import get_connection

class SaleDetailsModel:

    @staticmethod
    def get_sale_header(sale_id):
        conn = get_connection(sqlite3.Row)
        cur = conn.cursor()

        cur.execute("""
            SELECT sale_id, shop_id, date, grand_total
            FROM Sales
            WHERE sale_id = ?
        """, (sale_id,))

        row = cur.fetchone()
        conn.close()

        if not row:
            return None

        dt = datetime.fromisoformat(row["date"])

        return {
            "sale_id": row["sale_id"],
            "shop_id": row["shop_id"],
            "date": dt.strftime("%B %d, %Y %I:%M %p"),
            "grand_total": row["grand_total"]
        }

    @staticmethod
    def get_sale_items(sale_id):
        conn = get_connection(sqlite3.Row)
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                si.product_id,
                p.name AS product_name,
                si.quantity,
                si.price_per_unit,
                si.line_total
            FROM SaleItems si
            JOIN Products p ON p.product_id = si.product_id
            WHERE si.sale_id = ?
            ORDER BY p.name
        """, (sale_id,))

        rows = cur.fetchall()
        conn.close()
        return rows
