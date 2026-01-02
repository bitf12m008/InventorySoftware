import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QFrame,
    QGraphicsDropShadowEffect, QAction
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QIcon
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

        main_layout = QVBoxLayout(self)
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
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 80))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(24)

        title = QLabel("Welcome Back")
        title.setFont(QFont("Segoe UI Semibold", 24))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #222;")
        card_layout.addWidget(title)

        subtitle = QLabel("Sign in to continue")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #555; margin-top: -6px;")
        card_layout.addWidget(subtitle)

        user_label = QLabel("Username")
        user_label.setFont(QFont("Segoe UI", 11))
        user_label.setStyleSheet("color: #444;")
        card_layout.addWidget(user_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(44)
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 14px;
                border-radius: 8px;
                font-size: 14px;
                border: 1px solid #c9c9c9;
            }
            QLineEdit:focus {
                border: 1.4px solid #4A90E2;
            }
        """)
        card_layout.addWidget(self.username_input)

        pass_label = QLabel("Password")
        pass_label.setFont(QFont("Segoe UI", 11))
        pass_label.setStyleSheet("color: #444;")
        card_layout.addWidget(pass_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(44)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 42px 8px 14px;
                border-radius: 8px;
                font-size: 14px;
                border: 1px solid #c9c9c9;
            }
            QLineEdit:focus {
                border: 1.4px solid #4A90E2;
            }
        """)
        self.password_input.returnPressed.connect(self.handle_login)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(base_dir, "..", "assets")

        self.eye_show_icon = QIcon(os.path.join(assets_dir, "view.png"))
        self.eye_hide_icon = QIcon(os.path.join(assets_dir, "hide.png"))

        self.eye_action = QAction(self)
        self.eye_action.setIcon(self.eye_show_icon)
        self.eye_action.setToolTip("Show password")
        self.eye_action.triggered.connect(self.toggle_password_visibility)

        self.password_input.addAction(
            self.eye_action,
            QLineEdit.TrailingPosition
        )

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
            }
            QPushButton:hover {
                background: #3b7ac7;
            }
        """)
        login_btn.clicked.connect(self.handle_login)
        card_layout.addWidget(login_btn)

        main_layout.addWidget(card)

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.eye_action.setIcon(self.eye_hide_icon)
            self.eye_action.setToolTip("Hide password")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.eye_action.setIcon(self.eye_show_icon)
            self.eye_action.setToolTip("Show password")

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
