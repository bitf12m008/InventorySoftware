import sqlite3
from app.db.database_init import get_connection

class ShopModel:
    @staticmethod
    def get_all():
        conn = get_connection(sqlite3.Row)
        cur = conn.cursor()
        cur.execute("SELECT shop_id, shop_name FROM Shops ORDER BY shop_name")
        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def exists_name(name, exclude_shop_id=None):
        conn = get_connection()
        cur = conn.cursor()
        if exclude_shop_id is None:
            cur.execute(
                "SELECT 1 FROM Shops WHERE LOWER(shop_name)=?",
                (name.lower(),)
            )
        else:
            cur.execute(
                "SELECT 1 FROM Shops WHERE LOWER(shop_name)=? AND shop_id != ?",
                (name.lower(), exclude_shop_id)
            )
        exists = cur.fetchone() is not None
        conn.close()
        return exists

    @staticmethod
    def create(name):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO Shops (shop_name) VALUES (?)", (name,))
        shop_id = cur.lastrowid

        cur.execute("SELECT product_id FROM Products")
        product_rows = cur.fetchall()
        for (product_id,) in product_rows:
            cur.execute(
                """
                INSERT INTO Stock (product_id, shop_id, quantity)
                VALUES (?, ?, 0)
                ON CONFLICT(product_id, shop_id) DO UPDATE
                SET quantity = excluded.quantity
                """,
                (product_id, shop_id)
            )

        conn.commit()
        conn.close()
        return shop_id

    @staticmethod
    def update_name(shop_id, name):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE Shops SET shop_name=? WHERE shop_id=?",
            (name, shop_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_delete_blockers(shop_id):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM Sales WHERE shop_id=?", (shop_id,))
        sales_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM Purchases WHERE shop_id=?", (shop_id,))
        purchases_count = cur.fetchone()[0]

        cur.execute("SELECT COALESCE(SUM(quantity), 0) FROM Stock WHERE shop_id=?", (shop_id,))
        stock_qty = cur.fetchone()[0]

        conn.close()

        reasons = []
        if sales_count > 0:
            reasons.append("Sales exist for this shop.")
        if purchases_count > 0:
            reasons.append("Purchases exist for this shop.")
        if stock_qty > 0:
            reasons.append("Stock quantity is not zero for this shop.")
        return reasons

    @staticmethod
    def delete(shop_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM Stock WHERE shop_id=?", (shop_id,))
        cur.execute("DELETE FROM Shops WHERE shop_id=?", (shop_id,))
        conn.commit()
        conn.close()
