import sqlite3
from app.db.database_init import get_connection

class SaleItemModel:

    @staticmethod
    def create(sale_id, product_id, qty, price, subtotal):
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO SaleItems (sale_id, product_id, quantity, price_per_unit, line_total)
            VALUES (?, ?, ?, ?, ?)
        """, (sale_id, product_id, qty, price, subtotal))
        conn.commit()
        conn.close()
