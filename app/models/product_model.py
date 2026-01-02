import sqlite3
from app.db.database_init import DB_PATH

class ProductModel:

    @staticmethod
    def create(name):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO Products (name) VALUES (?)", (name,))
        product_id = c.lastrowid
        conn.commit()
        conn.close()
        return product_id

    @staticmethod
    def get_all():
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT product_id, name FROM Products ORDER BY name")
        rows = c.fetchall()
        conn.close()
        return rows

    @staticmethod
    def find_by_name(name):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "SELECT product_id FROM Products WHERE LOWER(name)=?",
            (name.lower(),)
        )
        row = c.fetchone()
        conn.close()
        return row[0] if row else None
    
    @staticmethod
    def get_by_shop(shop_id):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
            SELECT
                p.product_id,
                p.name AS product_name,
                s.quantity
            FROM Products p
            JOIN Stock s ON p.product_id = s.product_id
            WHERE s.shop_id = ?
            ORDER BY product_name COLLATE NOCASE ASC
        """, (shop_id,))

        rows = cur.fetchall()
        conn.close()
        return rows
    
    @staticmethod
    def get_by_id(product_id):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute(
            "SELECT product_id, name FROM Products WHERE product_id=?",
            (product_id,)
        )
        row = cur.fetchone()
        conn.close()
        return row

    @staticmethod
    def update_name(product_id, name):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute(
            "UPDATE Products SET name=? WHERE product_id=?",
            (name, product_id)
        )
        conn.commit()
        conn.close()
