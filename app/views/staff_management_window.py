from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QInputDialog
)
from PyQt5.QtGui import QFont, QColor

from app.controllers.staff_controller import StaffController
from app.views.add_staff_window import AddStaffWindow
from PyQt5.QtWidgets import QLineEdit

class StaffManagementWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = StaffController()
        self.setWindowTitle("Staff Management")
        self.resize(700, 450)
        self.setStyleSheet("background:#eef1f6;")
        self.setup_ui()
        self.load_staff()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Staff Management")
        title.setFont(QFont("Segoe UI Semibold", 20))
        layout.addWidget(title)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Username", "Role", "Status"]
        )
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {
                background:white;
                font-size:13px;
                border:none;
            }
            QHeaderView::section {
                background:#f0f3f8;
                padding:8px;
                font-weight:bold;
            }
        """)
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        add_btn = QPushButton("Add Staff")
        add_btn.clicked.connect(self.open_add_staff)

        reset_btn = QPushButton("Reset Password")
        reset_btn.clicked.connect(self.reset_password)

        delete_btn = QPushButton("Delete Staff")
        delete_btn.setStyleSheet("background:#d9534f;color:white;")
        delete_btn.clicked.connect(self.delete_staff)

        for b in (add_btn, reset_btn, delete_btn):
            b.setMinimumHeight(36)
            btn_row.addWidget(b)

        btn_row.addStretch()
        layout.addLayout(btn_row)

    def load_staff(self):
        staff = self.controller.get_all_staff()
        self.table.setRowCount(len(staff))

        for r, s in enumerate(staff):
            self.table.setItem(r, 0, QTableWidgetItem(str(s["id"])))
            self.table.setItem(r, 1, QTableWidgetItem(s["username"]))
            self.table.setItem(r, 2, QTableWidgetItem(s["role"]))

            status_item = QTableWidgetItem(s["status"])
            if s["status"] == "inactive":
                status_item.setForeground(QColor("#999"))
            self.table.setItem(r, 3, status_item)

    def open_add_staff(self):
        self.add_window = AddStaffWindow(on_success=self.load_staff)
        self.add_window.show()

    def delete_staff(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select", "Select a staff member.")
            return

        staff_id = int(self.table.item(row, 0).text())
        username = self.table.item(row, 1).text()

        confirm = QMessageBox.question(
            self,
            "Confirm",
            f"Deactivate staff '{username}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            self.controller.deactivate_staff(staff_id)
            self.load_staff()

    def reset_password(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select", "Select a staff member.")
            return

        staff_id = int(self.table.item(row, 0).text())

        pwd, ok = QInputDialog.getText(
            self,
            "Reset Password",
            "Enter new password:",
            echo=QLineEdit.Password
        )

        if ok and pwd:
            try:
                self.controller.reset_password(staff_id, pwd)
                QMessageBox.information(self, "Success", "Password reset successfully.")
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))
