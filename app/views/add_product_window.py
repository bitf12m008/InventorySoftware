from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QMessageBox, QListWidget, QListWidgetItem, QCheckBox,
    QFrame, QGraphicsDropShadowEffect, QStyle
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from app.controllers.product_controller import ProductController

class AddProductWindow(QWidget):
    def __init__(self, on_success=None):
        super().__init__()

        self.on_success = on_success
        self.controller = ProductController()

        self.setWindowTitle("Add New Product")
        self.setFixedSize(480, 560)
        self.setStyleSheet("background: #eef1f6;")

        self.setup_ui()
        self.load_shops()

    def setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(30, 30, 30, 30)
        main.setSpacing(20)
        main.setAlignment(Qt.AlignCenter)

        # ================= CARD =================
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(22)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 70))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(18)

        # ================= TITLE =================
        title = QLabel("Add Product")
        title.setFont(QFont("Segoe UI Semibold", 22))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #222;")
        card_layout.addWidget(title)

        subtitle = QLabel("Create a new product and assign it to shops")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666; margin-top: -6px;")
        card_layout.addWidget(subtitle)

        label_name = QLabel("Product Name")
        label_name.setFont(QFont("Segoe UI", 11))
        label_name.setStyleSheet("color: #444;")
        card_layout.addWidget(label_name)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter product name")
        self.name_input.setMinimumHeight(42)
        self.name_input.setStyleSheet("""
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
        card_layout.addWidget(self.name_input)

        label_shop = QLabel("Assign to Shops")
        label_shop.setFont(QFont("Segoe UI", 11))
        label_shop.setStyleSheet("color: #444;")
        card_layout.addWidget(label_shop)

        list_container = QFrame()
        list_container.setStyleSheet("""
            QFrame {
                background: #f7f9fc;
                border: 1px solid #d0d0d0;
                border-radius: 10px;
            }
        """)

        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(10, 10, 10, 10)

        self.shop_list = QListWidget()
        self.shop_list.setSelectionMode(QListWidget.NoSelection)
        self.shop_list.setStyleSheet("""
            QListWidget {
                border: none;
                background: transparent;
                font-size: 13px;
            }
        """)
        list_layout.addWidget(self.shop_list)

        card_layout.addWidget(list_container)

        # ================= ACTION BUTTON =================
        add_btn = QPushButton("Add Product")
        add_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogOkButton))
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setMinimumHeight(46)
        add_btn.setStyleSheet("""
            QPushButton {
                background: #4A90E2;
                color: white;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #3b7ac7;
            }
        """)
        add_btn.clicked.connect(self.save_product)
        card_layout.addSpacing(8)
        card_layout.addWidget(add_btn)

        main.addWidget(card)

    def load_shops(self):
        shops = self.controller.get_shops()
        self.shop_list.clear()

        for sid, name in shops:
            item = QListWidgetItem()
            checkbox = QCheckBox(name)
            checkbox.setFont(QFont("Segoe UI", 10))
            checkbox.setProperty("shop_id", sid)
            self.shop_list.addItem(item)
            self.shop_list.setItemWidget(item, checkbox)

    def save_product(self):
        name = self.name_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Missing Name", "Please enter a product name.")
            return

        selected_shop_ids = []
        for i in range(self.shop_list.count()):
            checkbox = self.shop_list.itemWidget(self.shop_list.item(i))
            if checkbox.isChecked():
                selected_shop_ids.append(checkbox.property("shop_id"))

        self.controller.create_product(name, selected_shop_ids)

        QMessageBox.information(self, "Success", "Product added successfully.")
        if self.on_success:
            self.on_success()
        self.close()
