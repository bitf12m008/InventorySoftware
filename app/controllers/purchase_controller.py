# app/controllers/purchase_controller.py

from app.models.shop_model import ShopModel
from app.models.product_model import ProductModel
from app.models.stock_model import StockModel
from app.models.purchase_model import PurchaseModel


class PurchaseController:

    def __init__(self):
        self.rows = []   # like a mini cart for purchase items

    # ----------------------
    # Loaders
    # ----------------------
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

    # ----------------------
    # Cart (Table Rows)
    # ----------------------
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

    # ----------------------
    # Save Purchase
    # ----------------------
    def save_purchase(self, shop_id):
        if not self.rows:
            raise ValueError("No purchase rows added.")

        for row in self.rows:
            name = row["name"]
            qty = row["qty"]
            price = row["price"]

            # 1. Ensure product exists
            product_id = self.find_product_by_name(name)
            if not product_id:
                product_id = ProductModel.create(name)
                StockModel.create(product_id, shop_id, 0)

            # 2. Save purchase
            PurchaseModel.create(product_id, shop_id, qty, price)

            # 3. Update stock
            StockModel.increase(product_id, shop_id, qty)

        # return number of rows saved or success flag
        return True
