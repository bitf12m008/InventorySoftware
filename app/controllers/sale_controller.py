from app.models.shop_model import ShopModel
from app.models.product_model import ProductModel
from app.models.sale_model import SaleModel
from app.models.stock_model import StockModel  # create if not exists
from datetime import datetime


class SaleController:
    def __init__(self):
        self.cart = []

    # ----------------------------
    # Shops & Products
    # ----------------------------
    def get_shops(self):
        return ShopModel.get_all()

    def get_products_for_shop(self, shop_id):
        return ProductModel.get_by_shop(shop_id)

    # ----------------------------
    # Cart Logic
    # ----------------------------
    def add_to_cart(self, product_id, name, price, qty, stock):
        if qty > stock:
            raise ValueError("Not enough stock")

        for item in self.cart:
            if item["product_id"] == product_id:
                new_qty = item["qty"] + qty
                if new_qty > stock:
                    raise ValueError("Not enough stock")
                item["qty"] = new_qty
                item["subtotal"] = item["qty"] * item["price"]
                return

        self.cart.append({
            "product_id": product_id,
            "name": name,
            "price": price,
            "qty": qty,
            "subtotal": price * qty
        })

    def remove_from_cart(self, index):
        if 0 <= index < len(self.cart):
            self.cart.pop(index)

    def clear_cart(self):
        self.cart.clear()

    def get_cart(self):
        return self.cart

    def get_total(self):
        return sum(i["subtotal"] for i in self.cart)

    # ----------------------------
    # Save Sale
    # ----------------------------
    def save_sale(self, shop_id):
        if not self.cart:
            raise ValueError("Cart is empty")

        # Validate stock again (critical)
        for item in self.cart:
            current = StockModel.get_quantity(item["product_id"], shop_id)
            if item["qty"] > current:
                raise ValueError(f"Insufficient stock for {item['name']}")

        sale_id = SaleModel.create_sale(
            shop_id=shop_id,
            date=datetime.now().isoformat(),
            items=self.cart
        )

        self.clear_cart()
        return sale_id
