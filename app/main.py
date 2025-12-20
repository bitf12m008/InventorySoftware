import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from app.views.login_window import LoginWindow
from app.db.database_init import initialize_database
from app.views.admin_dashboard import AdminDashboard

app_state = {}

class MainApp(QWidget):
    def __init__(self, user_info):
        super().__init__()
        self.user = user_info
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Dashboard")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        welcome = QLabel(f"Logged in as: {self.user['username']} ({self.user['role']})")
        welcome.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(welcome)

        self.setLayout(layout)


def main():
    initialize_database()
    app = QApplication(sys.argv)

    def on_login_success(user_info):
        if user_info.get("role") == "admin":
            app_state["admin"] = AdminDashboard(user_info)
            app_state["admin"].show()
        else:
            # load user-specific UI
            pass

    app_state["login"] = LoginWindow(on_login_success)
    app_state["login"].show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
