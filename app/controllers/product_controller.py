from app.models.product_model import ProductModel
from app.models.shop_model import ShopModel
from app.models.stock_model import StockModel

class ProductController:

    def get_shops(self):
        return ShopModel.get_all()

    def create_product(self, name, selected_shop_ids):
        product_id = ProductModel.create(name)

        for sid in selected_shop_ids:
            StockModel.create(product_id, sid, 0)

        return product_id
