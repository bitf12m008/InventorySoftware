from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from app.controllers.auth_controller import AuthController

class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Login - Inventory System")
        self.setFixedSize(480, 520)
        self.setStyleSheet("background: #e6e9ef;")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.94);
                border-radius: 18px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(26)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 80))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(24)

        title = QLabel("Welcome Back")
        title.setFont(QFont("Segoe UI Semibold", 24))
        title.setAlignment(Qt.AlignCenter)
        title.setMinimumHeight(40)
        title.setStyleSheet("color: #222;")
        card_layout.addWidget(title)

        subtitle = QLabel("Sign in to continue")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setMinimumHeight(30)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #555; margin-top: -6px;")
        card_layout.addWidget(subtitle)

        username_label = QLabel("Username")
        username_label.setFont(QFont("Segoe UI", 11))
        username_label.setMinimumHeight(22)
        username_label.setStyleSheet("color: #444;")
        card_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(44)
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 14px;
                border-radius: 8px;
                font-size: 14px;
                border: 1px solid #c9c9c9;
                background: white;
            }
            QLineEdit:focus {
                border: 1.4px solid #4A90E2;
            }
        """)
        card_layout.addWidget(self.username_input)

        password_label = QLabel("Password")
        password_label.setFont(QFont("Segoe UI", 11))
        password_label.setMinimumHeight(22)
        password_label.setStyleSheet("color: #444;")
        card_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(44)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 14px;
                border-radius: 8px;
                font-size: 14px;
                border: 1px solid #c9c9c9;
                background: white;
            }
            QLineEdit:focus {
                border: 1.4px solid #4A90E2;
            }
        """)
        card_layout.addWidget(self.password_input)

        login_btn = QPushButton("Sign In")
        login_btn.setMinimumHeight(46)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setStyleSheet("""
            QPushButton {
                background: #4A90E2;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 0.3px;
            }
            QPushButton:hover {
                background: #3b7ac7;
            }
        """)
        login_btn.clicked.connect(self.handle_login)
        card_layout.addWidget(login_btn)

        card.setLayout(card_layout)
        main_layout.addWidget(card)
        self.setLayout(main_layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password.")
            return

        user = AuthController.login(username, password)

        if user:
            self.on_login_success(user)
            self.close()
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password.")
