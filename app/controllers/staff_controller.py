from app.models.user_model import UserModel
import hashlib

class StaffController:
    def __init__(self):
        self.model = UserModel()

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

    def get_all_staff(self):
        return self.model.get_all_staff()

    def add_staff(self, username, password):
        hashed = self._hash_password(password)
        self.model.create_user(username, hashed, role="staff")

    def deactivate_staff(self, staff_id):
        self.model.deactivate_user(staff_id)

    def reset_password(self, staff_id, new_password):
        hashed = self._hash_password(new_password)
        self.model.update_password(staff_id, hashed)

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
