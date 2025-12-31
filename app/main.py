import sys
import atexit
from PyQt5.QtWidgets import QApplication
from app.db.database_init import initialize_database
from app.views.login_window import LoginWindow
from app.views.admin_dashboard import AdminDashboard
from app.views.staff_dashboard import StaffDashboard
from app.controllers.backup_controller import BackupController

app_state = {}

def main():
    initialize_database()
    app = QApplication(sys.argv)

    def on_login_success(user_info):
        app_state["login"].close()

        role = user_info.get("role")

        if role == "admin":
            app_state["admin"] = AdminDashboard(user_info)
            app_state["admin"].show()

        elif role == "staff":
            app_state["staff"] = StaffDashboard(user_info)
            app_state["staff"].show()

        else:
            raise ValueError("Unknown user role")

    app_state["login"] = LoginWindow(on_login_success)
    app_state["login"].show()

    sys.exit(app.exec_())

atexit.register(lambda: BackupController.backup_if_changed())

if __name__ == "__main__":
    main()
