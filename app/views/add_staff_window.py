# app/views/add_staff_window.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from app.controllers.staff_controller import StaffController

class AddStaffWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add Staff Account")
        self.setFixedSize(460, 350)
        self.setStyleSheet("background: #eef1f6;")

        self.setup_ui()

    def setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(32, 32, 32, 32)
        main.setAlignment(Qt.AlignTop)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 60))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        # layout.setContentsMargins(32, 36, 32, 36)
        layout.setSpacing(0)

        title = QLabel("Create Staff Account")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setMinimumHeight(40)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #222; padding-top: 2px;")
        layout.addWidget(title)

        subtitle = QLabel("Staff users can only access sales features")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setMinimumHeight(24)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666;")
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        user_label = QLabel("Username")
        user_label.setFont(QFont("Segoe UI", 11))
        user_label.setMinimumHeight(22)
        user_label.setStyleSheet("color: #444;")
        layout.addWidget(user_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter staff username")
        self.username_input.setMinimumHeight(42)
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 14px;
                border-radius: 8px;
                font-size: 14px;
                border: 1px solid #c9c9c9;
                background: white;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;  /* thicker focus border */
            }
        """)
        layout.addWidget(self.username_input)

        layout.addSpacing(18)

        pass_label = QLabel("Password")
        pass_label.setFont(QFont("Segoe UI", 11))
        pass_label.setMinimumHeight(22)
        pass_label.setStyleSheet("color: #444;")
        layout.addWidget(pass_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(42)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 14px;
                border-radius: 8px;
                font-size: 14px;
                border: 1px solid #c9c9c9;
                background: white;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
            }
        """)
        layout.addWidget(self.password_input)

        create_btn = QPushButton("Create Staff")
        create_btn.setCursor(Qt.PointingHandCursor)
        create_btn.setMinimumHeight(46)
        create_btn.setStyleSheet("""
            QPushButton {
                background: #4A90E2;
                color: white;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
                margin-top: 20px;
            }
            QPushButton:hover {
                background: #3b7ac7;
            }
        """)
        create_btn.clicked.connect(self.create_staff)
        layout.addWidget(create_btn)

        main.addWidget(card)

    def create_staff(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        try:
            StaffController.create_staff(username, password)
            QMessageBox.information(
                self,
                "Success",
                "Staff account created successfully"
            )
            self.close()

        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to create staff:\n{e}"
            )
