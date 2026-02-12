import sqlite3
from app.db.database_init import get_connection

class ProductModel:

    @staticmethod
    def create(name):
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO Products (name) VALUES (?)", (name,))
        product_id = c.lastrowid
        conn.commit()
        conn.close()
        return product_id

    @staticmethod
    def get_all():
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT product_id, name FROM Products ORDER BY name")
        rows = c.fetchall()
        conn.close()
        return rows

    @staticmethod
    def find_by_name(name):
        conn = get_connection()
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
        conn = get_connection(sqlite3.Row)
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
        conn = get_connection(sqlite3.Row)
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
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "UPDATE Products SET name=? WHERE product_id=?",
            (name, product_id)
        )
        conn.commit()
        conn.close()
