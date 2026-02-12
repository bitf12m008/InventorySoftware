import sqlite3
from app.models.shop_model import ShopModel
from app.models.product_model import ProductModel
from app.models.stock_model import StockModel
from app.models.purchase_model import PurchaseModel
from app.models.audit_log_model import AuditLogModel
from app.db.database_init import get_connection

class PurchaseController:

    def __init__(self, actor=None):
        self.rows = []
        self.actor = actor or {}

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

                cur.execute(
                    """
                    SELECT quantity
                    FROM Stock
                    WHERE product_id = ? AND shop_id = ?
                    """,
                    (product_id, shop_id)
                )
                stock_row = cur.fetchone()
                old_stock = stock_row[0] if stock_row else 0

                purchase_id = PurchaseModel.create_with_cursor(
                    cur, product_id, shop_id, qty, price
                )
                StockModel.increase_with_cursor(
                    cur, product_id, shop_id, qty
                )
                new_stock = old_stock + qty

                AuditLogModel.create_with_cursor(
                    cursor=cur,
                    action="PURCHASE_ADD",
                    entity_type="Purchase",
                    entity_id=purchase_id,
                    shop_id=shop_id,
                    product_id=product_id,
                    user_id=self.actor.get("user_id"),
                    username=self.actor.get("username"),
                    details=(
                        f"{name}: qty={qty}, unit_price={price:.2f}, "
                        f"stock {old_stock} -> {new_stock}"
                    ),
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
