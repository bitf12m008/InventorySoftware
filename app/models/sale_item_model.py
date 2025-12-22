import sqlite3
from app.db.database_init import DB_PATH


class SaleItemModel:

    @staticmethod
    def create(sale_id, product_id, qty, price, subtotal):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO SaleItems (sale_id, product_id, quantity, price_per_unit, line_total)
            VALUES (?, ?, ?, ?, ?)
        """, (sale_id, product_id, qty, price, subtotal))
        conn.commit()
        conn.close()
