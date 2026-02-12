from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCheckBox, QPushButton,
    QMessageBox, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from app.controllers.staff_controller import StaffController

PERMISSION_LABELS = {
    "add_sale": "Add Sale",
    "add_purchase": "Add Purchase",
    "show_sales": "Show Sales",
    "view_profit_report": "View Profit Report",
    "view_weekly_profit": "View Weekly Profit",
}


class StaffPermissionsWindow(QWidget):
    def __init__(self, staff_id, staff_username, actor=None, on_success=None):
        super().__init__()
        self.staff_id = staff_id
        self.staff_username = staff_username
        self.on_success = on_success
        self.controller = StaffController(actor=actor or {})
        self.checks = {}

        self.setWindowTitle(f"Permissions - {staff_username}")
        self.setFixedSize(520, 470)
        self.setStyleSheet("background:#eef1f6;")
        self.setup_ui()
        self.load_permissions()

    def setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(26, 26, 26, 26)
        main.setSpacing(14)

        card = QFrame()
        card.setStyleSheet("QFrame { background: white; border-radius: 14px; }")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 60))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("Staff Permissions")
        title.setFont(QFont("Segoe UI Semibold", 18))
        title.setStyleSheet("color:#222;")
        layout.addWidget(title)

        subtitle = QLabel(f"User: {self.staff_username}")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color:#666;")
        layout.addWidget(subtitle)

        for key in self.controller.get_permission_catalog():
            cb = QCheckBox(PERMISSION_LABELS.get(key, key))
            cb.setProperty("permission_key", key)
            cb.setFont(QFont("Segoe UI", 11))
            cb.setStyleSheet("QCheckBox { padding: 5px 0; color:#222; }")
            self.checks[key] = cb
            layout.addWidget(cb)

        save_btn = QPushButton("Save Permissions")
        save_btn.setMinimumHeight(42)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #4A90E2;
                color: white;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #3b7ac7;
            }
        """)
        save_btn.clicked.connect(self.save_permissions)
        layout.addWidget(save_btn)

        main.addWidget(card)

    def load_permissions(self):
        granted = set(self.controller.get_staff_permissions(self.staff_id))
        for key, check in self.checks.items():
            check.setChecked(key in granted)

    def save_permissions(self):
        selected = [k for k, c in self.checks.items() if c.isChecked()]
        try:
            self.controller.update_staff_permissions(self.staff_id, selected)
            QMessageBox.information(self, "Saved", "Permissions updated.")
            if self.on_success:
                self.on_success()
            self.close()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
