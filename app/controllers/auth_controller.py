from app.models.user_model import UserModel


class AuthController:

    @staticmethod
    def login(username, password):
        return UserModel.authenticate(username, password)
