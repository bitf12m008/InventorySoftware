import sqlite3
from app.db.database_init import DB_PATH


class SaleModel:

    @staticmethod
    def create(shop_id, total, date):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO Sales (shop_id, date, grand_total) VALUES (?, ?, ?)",
            (shop_id, date, total)
        )
        sale_id = c.lastrowid
        conn.commit()
        conn.close()
        return sale_id
    
    @staticmethod
    def last_price(product_id, shop_id):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT si.price_per_unit
            FROM SaleItems si
            JOIN Sales s ON s.sale_id = si.sale_id
            WHERE si.product_id=? AND s.shop_id=?
            ORDER BY si.sale_item_id DESC
            LIMIT 1
        """, (product_id, shop_id))
        row = cur.fetchone()
        conn.close()
        return row["price_per_unit"] if row else None
    
    @staticmethod
    def get_sales_by_shop_and_date(shop_id, start_date, end_date):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
            SELECT sale_id, date, grand_total
            FROM Sales
            WHERE shop_id = ?
              AND date(date) BETWEEN date(?) AND date(?)
            ORDER BY sale_id DESC
        """, (shop_id, start_date, end_date))

        rows = cur.fetchall()
        conn.close()
        return rows
