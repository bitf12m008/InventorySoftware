import sqlite3
from app.db.database_init import DB_PATH

class StockModel:

    @staticmethod
    def create(product_id, shop_id, quantity=0):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO Stock (product_id, shop_id, quantity) VALUES (?, ?, ?)",
            (product_id, shop_id, quantity)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def increase(product_id, shop_id, qty):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "UPDATE Stock SET quantity = quantity + ? WHERE product_id=? AND shop_id=?",
            (qty, product_id, shop_id)
        )

        if c.rowcount == 0:
            c.execute(
                "INSERT INTO Stock (product_id, shop_id, quantity) VALUES (?, ?, ?)",
                (product_id, shop_id, qty)
            )

        conn.commit()
        conn.close()

    @staticmethod
    def get_for_product(product_id, shop_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "SELECT quantity FROM Stock WHERE product_id=? AND shop_id=?",
            (product_id, shop_id)
        )
        row = c.fetchone()
        conn.close()
        return row[0] if row else 0

    @staticmethod
    def reduce(product_id, shop_id, qty):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "UPDATE Stock SET quantity = quantity - ? WHERE product_id=? AND shop_id=?",
            (qty, product_id, shop_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_products_for_shop(shop_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT p.product_id, p.name, s.quantity
            FROM Products p
            JOIN Stock s ON p.product_id = s.product_id
            WHERE s.shop_id = ?
            ORDER BY p.name
        """, (shop_id,))
        rows = c.fetchall()
        conn.close()
        return rows
    
    @staticmethod
    def get_quantity(product_id, shop_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "SELECT quantity FROM Stock WHERE product_id=? AND shop_id=?",
            (product_id, shop_id)
        )
        row = c.fetchone()
        conn.close()
        return row[0] if row else 0

    @staticmethod
    def set_quantity(product_id, shop_id, quantity):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "UPDATE Stock SET quantity=? WHERE product_id=? AND shop_id=?",
            (quantity, product_id, shop_id)
        )

        if c.rowcount == 0:
            c.execute(
                "INSERT INTO Stock (product_id, shop_id, quantity) VALUES (?, ?, ?)",
                (product_id, shop_id, quantity)
            )

        conn.commit()
        conn.close()
