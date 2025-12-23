from app.models.shop_model import ShopModel
from app.models.product_model import ProductModel
from app.models.purchase_model import PurchaseModel
from app.models.sale_model import SaleModel

class DashboardController:
    def __init__(self):
        pass

    # ----------------------------
    # Shops
    # ----------------------------
    def get_shops(self):
        return ShopModel.get_all()

    # ----------------------------
    # Products + Calculations
    # ----------------------------
    def get_products_for_shop(self, shop_id):
        products = ProductModel.get_by_shop(shop_id)

        enriched = []

        for p in products:
            pid = p["product_id"]

            avg_cost = PurchaseModel.avg_price(pid, shop_id)
            last_purchase = PurchaseModel.last_price(pid, shop_id)
            last_sale = SaleModel.last_price(pid, shop_id)

            if last_purchase is None or last_sale is None:
                profit = None
            else:
                profit = last_sale - last_purchase

            enriched.append({
                "product_id": pid,
                "product_name": p["product_name"],
                "quantity": p["quantity"],
                "avg_cost": avg_cost,
                "last_purchase": last_purchase,
                "last_sale": last_sale,
                "profit": profit
            })

        return enriched
