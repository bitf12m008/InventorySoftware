import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from app.login_window import LoginWindow
from app.database_init import initialize_database

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
        main_window = MainApp(user_info)
        main_window.show()

    login = LoginWindow(on_login_success)
    login.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
