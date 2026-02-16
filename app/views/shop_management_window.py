from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from app.controllers.shop_controller import ShopController


class ShopManagementWindow(QDialog):
    def __init__(self, on_updated=None):
        super().__init__()
        self.on_updated = on_updated
        self.controller = ShopController()
        self._selected_shop_id = None
        self.setup_ui()
        self.load_shops()

    def setup_ui(self):
        self.setWindowTitle("Manage Shops")
        self.setFixedSize(520, 480)
        self.setStyleSheet("background: #eef1f6;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        title = QLabel("Manage Shops")
        title.setFont(QFont("Segoe UI Semibold", 18))
        title.setStyleSheet("color: #222;")
        main_layout.addWidget(title)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)

        self.shop_list = QListWidget()
        self.shop_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                padding: 6px;
                background: #fafafa;
            }
            QListWidget::item {
                padding: 8px 10px;
            }
            QListWidget::item:selected {
                background: #dbeafe;
                color: #111;
            }
        """)
        self.shop_list.itemSelectionChanged.connect(self.on_shop_selected)
        card_layout.addWidget(self.shop_list)

        form_row = QHBoxLayout()
        name_label = QLabel("Shop Name")
        name_label.setFont(QFont("Segoe UI", 10))
        name_label.setStyleSheet("color: #444;")
        form_row.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter shop name")
        self.name_input.setMinimumHeight(36)
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 6px 10px;
                border-radius: 8px;
                border: 1px solid #c9c9c9;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1.4px solid #4A90E2;
            }
        """)
        form_row.addWidget(self.name_input, stretch=1)
        card_layout.addLayout(form_row)

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("Add Shop")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setMinimumHeight(40)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: #4A90E2;
                color: white;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 14px;
            }
            QPushButton:hover { background: #3b7ac7; }
        """)
        self.add_btn.clicked.connect(self.add_shop)
        btn_row.addWidget(self.add_btn)

        self.rename_btn = QPushButton("Rename Shop")
        self.rename_btn.setCursor(Qt.PointingHandCursor)
        self.rename_btn.setMinimumHeight(40)
        self.rename_btn.setStyleSheet("""
            QPushButton {
                background: #0ea5a6;
                color: white;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 14px;
            }
            QPushButton:hover { background: #0b8b8c; }
            QPushButton:disabled { background: #9bd6d6; color: #f2f7f7; }
        """)
        self.rename_btn.setEnabled(False)
        self.rename_btn.clicked.connect(self.rename_shop)
        btn_row.addWidget(self.rename_btn)

        self.delete_btn = QPushButton("Delete Shop")
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.setMinimumHeight(40)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background: #dc2626;
                color: white;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 14px;
            }
            QPushButton:hover { background: #b91c1c; }
            QPushButton:disabled { background: #f1a3a3; color: #fff7f7; }
        """)
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_shop)
        btn_row.addWidget(self.delete_btn)

        btn_row.addStretch()
        card_layout.addLayout(btn_row)

        main_layout.addWidget(card)

    def load_shops(self, keep_selected_id=None):
        self.shop_list.clear()
        shops = self.controller.get_shops()
        for s in shops:
            item = QListWidgetItem(s["shop_name"])
            item.setData(Qt.UserRole, s["shop_id"])
            self.shop_list.addItem(item)

        if keep_selected_id is not None:
            for i in range(self.shop_list.count()):
                item = self.shop_list.item(i)
                if item.data(Qt.UserRole) == keep_selected_id:
                    item.setSelected(True)
                    break

    def on_shop_selected(self):
        items = self.shop_list.selectedItems()
        if not items:
            self._selected_shop_id = None
            self.rename_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return
        item = items[0]
        self._selected_shop_id = item.data(Qt.UserRole)
        self.name_input.setText(item.text())
        self.rename_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

    def add_shop(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Name", "Enter a shop name.")
            return
        if self.controller.exists_name(name):
            QMessageBox.warning(self, "Duplicate Name", "A shop with that name already exists.")
            return

        self.controller.create_shop(name)
        self.name_input.clear()
        self.load_shops()
        self._notify_updated()

    def rename_shop(self):
        if self._selected_shop_id is None:
            QMessageBox.warning(self, "No Selection", "Select a shop to rename.")
            return
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Name", "Enter a shop name.")
            return
        if self.controller.exists_name(name, exclude_shop_id=self._selected_shop_id):
            QMessageBox.warning(self, "Duplicate Name", "A shop with that name already exists.")
            return

        self.controller.update_shop_name(self._selected_shop_id, name)
        self.load_shops(keep_selected_id=self._selected_shop_id)
        self._notify_updated()

    def delete_shop(self):
        if self._selected_shop_id is None:
            QMessageBox.warning(self, "No Selection", "Select a shop to delete.")
            return

        blockers = self.controller.get_delete_blockers(self._selected_shop_id)
        if blockers:
            msg = "Cannot delete this shop:\n- " + "\n- ".join(blockers)
            QMessageBox.warning(self, "Delete Blocked", msg)
            return

        name = self.name_input.text().strip() or "this shop"
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete '{name}'? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        self.controller.delete_shop(self._selected_shop_id)
        self._selected_shop_id = None
        self.name_input.clear()
        self.rename_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.load_shops()
        self._notify_updated()

    def _notify_updated(self):
        if self.on_updated:
            self.on_updated()
