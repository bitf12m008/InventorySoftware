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
