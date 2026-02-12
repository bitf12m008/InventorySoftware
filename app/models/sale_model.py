import sqlite3
from datetime import datetime
from app.db.database_init import get_connection

class SaleModel:

    @staticmethod
    def create(shop_id, total, date):
        conn = get_connection()
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
        conn = get_connection(sqlite3.Row)
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
        conn = get_connection(sqlite3.Row)
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
        formatted = []
        for r in rows:
            dt = datetime.fromisoformat(r["date"])
            formatted.append({
                "sale_id": r["sale_id"],
                "date": dt.strftime("%B %d, %Y %I:%M %p"),
                "grand_total": r["grand_total"]
            })

        return formatted
    
    @staticmethod
    def create_sale(shop_id, date, items):
        conn = get_connection()
        cur = conn.cursor()

        grand_total = sum(i["subtotal"] for i in items)

        cur.execute(
            "INSERT INTO Sales (shop_id, date, grand_total) VALUES (?, ?, ?)",
            (shop_id, date, grand_total)
        )
        sale_id = cur.lastrowid

        for item in items:
            cur.execute("""
                INSERT INTO SaleItems
                (sale_id, product_id, quantity, price_per_unit, line_total)
                VALUES (?, ?, ?, ?, ?)
            """, (
                sale_id,
                item["product_id"],
                item["qty"],
                item["price"],
                item["subtotal"]
            ))

            cur.execute("""
                UPDATE Stock
                SET quantity = quantity - ?
                WHERE product_id = ? AND shop_id = ?
            """, (item["qty"], item["product_id"], shop_id))

        conn.commit()
        conn.close()
        return sale_id
