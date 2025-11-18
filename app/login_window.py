from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from auth_service import AuthService


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Login - Inventory System")
        self.setFixedSize(350, 220)

        layout = QVBoxLayout()

        title = QLabel("Inventory Login")
        title.setFont(QFont("Arial", 16))
        title.setStyleSheet("margin-bottom: 15px; font-weight: bold; text-align: center;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.handle_login)
        login_btn.setStyleSheet("padding: 8px; font-size: 14px;")
        layout.addWidget(login_btn)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password.")
            return

        user = AuthService.login(username, password)

        if user:
            QMessageBox.information(self, "Success", f"Welcome, {user['username']}!")
            self.on_login_success(user)   # pass user info to main app
            self.close()
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password.")
