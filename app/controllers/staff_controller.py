import hashlib
from app.models.user_model import UserModel

class StaffController:
    @staticmethod
    def create_staff(username: str, password: str):
        username = username.strip()

        if not username or not password:
            raise ValueError("Username and password are required")

        if len(password) < 4:
            raise ValueError("Password must be at least 4 characters")

        if UserModel.exists(username):
            raise ValueError("Username already exists")

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        UserModel.create(
            username=username,
            password_hash=password_hash,
            role="staff"
        )
