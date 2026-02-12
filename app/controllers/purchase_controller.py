import sqlite3
from app.models.shop_model import ShopModel
from app.models.product_model import ProductModel
from app.models.stock_model import StockModel
from app.models.purchase_model import PurchaseModel
from app.db.database_init import get_connection

class PurchaseController:

    def __init__(self):
        self.rows = []

    def get_shops(self):
        return ShopModel.get_all()

    def get_products(self):
        return ProductModel.get_all()

    def find_product_by_name(self, name):
        name = name.lower().strip()
        products = self.get_products()
        for pid, pname in products:
            if pname.lower() == name:
                return pid
        return None

    def add_row(self, name, qty, price):
        self.rows.append({
            "name": name.strip(),
            "qty": qty,
            "price": price
        })

    def remove_row(self, index):
        if 0 <= index < len(self.rows):
            self.rows.pop(index)

    def calculate_totals(self):
        return sum(r["qty"] * r["price"] for r in self.rows)

    def get_rows(self):
        return self.rows

    def save_purchase(self, shop_id):
        if not self.rows:
            raise ValueError("No purchase rows added.")

        conn = get_connection()
        cur = conn.cursor()

        try:
            for row in self.rows:
                name = row["name"].strip()
                qty = int(row["qty"])
                price = float(row["price"])

                if not name:
                    raise ValueError("Product name is required.")
                if qty <= 0:
                    raise ValueError("Quantity must be greater than 0.")
                if price < 0:
                    raise ValueError("Price cannot be negative.")

                cur.execute(
                    "SELECT product_id FROM Products WHERE LOWER(name) = ?",
                    (name.lower(),)
                )
                existing = cur.fetchone()
                if existing:
                    product_id = existing[0]
                else:
                    cur.execute(
                        "INSERT INTO Products (name) VALUES (?)",
                        (name,)
                    )
                    product_id = cur.lastrowid

                PurchaseModel.create_with_cursor(
                    cur, product_id, shop_id, qty, price
                )
                StockModel.increase_with_cursor(
                    cur, product_id, shop_id, qty
                )

            conn.commit()
        except (ValueError, sqlite3.IntegrityError):
            conn.rollback()
            raise
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        return True
