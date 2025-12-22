import sqlite3
from app.db.database_init import DB_PATH


class SaleDetailsModel:

    @staticmethod
    def get_sale_header(sale_id):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
            SELECT sale_id, shop_id, date, grand_total
            FROM Sales
            WHERE sale_id = ?
        """, (sale_id,))

        row = cur.fetchone()
        conn.close()
        return row

    @staticmethod
    def get_sale_items(sale_id):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
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
