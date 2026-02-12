from app.models.user_model import UserModel
from app.models.audit_log_model import AuditLogModel

class StaffController:
    def __init__(self, actor=None):
        self.model = UserModel()
        self.actor = actor or {}

    def _actor_id(self):
        return self.actor.get("user_id")

    def _actor_name(self):
        return self.actor.get("username")

    def create_staff(self, username: str, password: str):
        username = username.strip()

        if not username or not password:
            raise ValueError("Username and password are required")

        if len(password) < 4:
            raise ValueError("Password must be at least 4 characters")

        if UserModel.exists(username):
            raise ValueError("Username already exists")

        password_hash = UserModel.hash_password(password)

        created_user_id = UserModel.create(
            username=username,
            password_hash=password_hash,
            role="staff"
        )
        AuditLogModel.log(
            action="USER_CREATE",
            entity_type="User",
            entity_id=created_user_id,
            user_id=self._actor_id(),
            username=self._actor_name(),
            details=f"Created staff account '{username}'",
        )

    def get_all_staff(self):
        return self.model.get_all_staff()

    def add_staff(self, username, password):
        self.create_staff(username, password)

    def deactivate_staff(self, staff_id):
        target = self.model.get_by_id(staff_id)
        self.model.deactivate_user(staff_id)
        target_name = target["username"] if target else f"user_id={staff_id}"
        AuditLogModel.log(
            action="USER_DEACTIVATE",
            entity_type="User",
            entity_id=staff_id,
            user_id=self._actor_id(),
            username=self._actor_name(),
            details=f"Deactivated user '{target_name}'",
        )

    def reset_password(self, staff_id, new_password):
        if not new_password or len(new_password) < 4:
            raise ValueError("Password must be at least 4 characters")
        hashed = self._hash_password(new_password)
        self.model.update_password(staff_id, hashed)
        target = self.model.get_by_id(staff_id)
        target_name = target["username"] if target else f"user_id={staff_id}"
        AuditLogModel.log(
            action="USER_PASSWORD_RESET",
            entity_type="User",
            entity_id=staff_id,
            user_id=self._actor_id(),
            username=self._actor_name(),
            details=f"Reset password for '{target_name}'",
        )

    def _hash_password(self, password):
        return UserModel.hash_password(password)
