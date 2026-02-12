import sqlite3
from app.db.database_init import get_connection

class PurchaseModel:

    @staticmethod
    def create(product_id, shop_id, qty, price):
        total = qty * price
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Purchases (product_id, shop_id, quantity, price, total, date)
            VALUES (?, ?, ?, ?, ?, date('now'))
        """, (product_id, shop_id, qty, price, total))
        purchase_id = cur.lastrowid
        conn.commit()
        conn.close()
        return purchase_id

    @staticmethod
    def create_with_cursor(cur, product_id, shop_id, qty, price):
        total = qty * price
        cur.execute("""
            INSERT INTO Purchases (product_id, shop_id, quantity, price, total, date)
            VALUES (?, ?, ?, ?, ?, date('now'))
        """, (product_id, shop_id, qty, price, total))
        return cur.lastrowid

    @staticmethod
    def last_price(product_id, shop_id):
        conn = get_connection(sqlite3.Row)
        cur = conn.cursor()
        cur.execute("""
            SELECT price FROM Purchases
            WHERE product_id=? AND shop_id=?
            ORDER BY purchase_id DESC
            LIMIT 1
        """, (product_id, shop_id))
        row = cur.fetchone()
        conn.close()
        return row["price"] if row else None

    @staticmethod
    def avg_price(product_id, shop_id):
        conn = get_connection(sqlite3.Row)
        cur = conn.cursor()
        cur.execute("""
            SELECT SUM(quantity * price) AS total_cost,
                   SUM(quantity) AS total_qty
            FROM Purchases
            WHERE product_id=? AND shop_id=?
        """, (product_id, shop_id))
        row = cur.fetchone()
        conn.close()
        if row and row["total_qty"]:
            return row["total_cost"] / row["total_qty"]
        return None
