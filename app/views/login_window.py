# app/login_window.py

from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QHBoxLayout, QFrame, QStyle
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from app.models.user_model import UserModel

class AuthController:

    @staticmethod
    def login(username, password):
        return UserModel.authenticate(username, password)



class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Login - Inventory System")
        self.setFixedSize(380, 300)
        self.setStyleSheet("background-color: #f4f4f4;")

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        # -------- Card Container --------
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                padding: 8px;
                border: 1px solid #d0d0d0;
                height: 30px;
            }
        """)
        card_layout = QVBoxLayout()

        # -------- Title with built-in icon --------
        title_layout = QHBoxLayout()

        # icon_label = QLabel()
        # icon_label.setPixmap(self.style().standardIcon(QStyle.SP_DesktopIcon).pixmap(32, 32))
        # title_layout.addWidget(icon_label)

        title = QLabel("Inventory Login")
        title.setFont(QFont("Arial", 18))
        title.setStyleSheet("font-weight: bold; color: #333;")
        title.setAlignment(Qt.AlignCenter)

        # Ensure enough space so the label doesn't get cropped
        title.setMinimumHeight(20)

        title_layout.addWidget(title)


        card_layout.addLayout(title_layout)
        card_layout.addSpacing(10)

        # -------- Username Input --------
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 6px;
                border: 1px solid #b5b5b5;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d4;
            }
        """)
        card_layout.addWidget(self.username_input)

        # -------- Password Input --------
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 6px;
                border: 1px solid #b5b5b5;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d4;
            }
        """)
        card_layout.addWidget(self.password_input)

        # -------- Login Button --------
        login_btn = QPushButton("Login")
        login_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogOkButton))
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                padding: 10px;
                font-size: 15px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
        """)
        login_btn.clicked.connect(self.handle_login)
        card_layout.addWidget(login_btn)

        card.setLayout(card_layout)
        layout.addWidget(card)

        self.setLayout(layout)

    # -------- Login Logic --------
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(
                self,
                "Error",
                "Please enter both username and password."
            )
            return

        user = AuthController.login(username, password)

        if user:
            QMessageBox.information(
                self,
                "Success",
                f"Welcome, {user['username']}!"
            )
            self.on_login_success(user)
            self.close()
        else:
            QMessageBox.critical(
                self,
                "Login Failed",
                "Invalid username or password."
            )
