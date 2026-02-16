from app.models.shop_model import ShopModel


class ShopController:
    def get_shops(self):
        return ShopModel.get_all()

    def create_shop(self, name):
        return ShopModel.create(name)

    def update_shop_name(self, shop_id, name):
        ShopModel.update_name(shop_id, name)

    def exists_name(self, name, exclude_shop_id=None):
        return ShopModel.exists_name(name, exclude_shop_id)

    def get_delete_blockers(self, shop_id):
        return ShopModel.get_delete_blockers(shop_id)

    def delete_shop(self, shop_id):
        ShopModel.delete(shop_id)
