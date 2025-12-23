import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from app.db.database_init import initialize_database
from app.views.login_window import LoginWindow
from app.views.admin_dashboard import AdminDashboard

app_state = {}

def main():
    initialize_database()
    app = QApplication(sys.argv)

    def on_login_success(user_info):
        if user_info.get("role") == "admin":
            app_state["admin"] = AdminDashboard(user_info)
            app_state["admin"].show()
        else:
            pass

    app_state["login"] = LoginWindow(on_login_success)
    app_state["login"].show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
