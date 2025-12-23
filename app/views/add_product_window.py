# app/views/add_product_window.py

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QMessageBox, QListWidget, QListWidgetItem, QCheckBox,
    QFrame, QStyle, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from app.controllers.product_controller import ProductController


class AddProductWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.controller = ProductController()

        self.setWindowTitle("Add New Product")
        self.setFixedSize(440, 500)
        self.setStyleSheet("background-color: #f2f3f5;")

        self.setup_ui()
        self.load_shops()

    # -------------------------------------------------
    # UI (unchanged)
    # -------------------------------------------------
    def setup_ui(self):
        main = QVBoxLayout()
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(15)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                border: 1px solid #cccccc;
            }
        """)
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(22, 22, 22, 22)
        card_layout.setSpacing(14)

        title = QLabel("Add Product")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)

        subtitle = QLabel("Create a new product and assign it to shops")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666;")
        card_layout.addWidget(subtitle)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #e1e1e1; margin-bottom: 5px;")
        card_layout.addWidget(sep)

        label_name = QLabel("Product Name")
        label_name.setFont(QFont("Segoe UI", 11))
        card_layout.addWidget(label_name)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter product name")
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 9px;
                border-radius: 6px;
                border: 1px solid #bfc3c7;
                background: #fafafa;
            }
            QLineEdit:focus {
                border: 1px solid #0078d4;
                background: white;
            }
        """)
        card_layout.addWidget(self.name_input)

        # Shop assignment
        label_shop = QLabel("Assign to Shops")
        label_shop.setFont(QFont("Segoe UI", 11))
        card_layout.addWidget(label_shop)

        list_container = QFrame()
        list_container.setStyleSheet("""
            QFrame {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                background: #f7f7f7;
            }
        """)
        list_layout = QVBoxLayout()
        list_layout.setContentsMargins(4, 4, 4, 4)

        self.shop_list = QListWidget()
        self.shop_list.setSelectionMode(QListWidget.NoSelection)
        list_layout.addWidget(self.shop_list)
        list_container.setLayout(list_layout)
        card_layout.addWidget(list_container)

        # Save button
        add_btn = QPushButton("Add Product")
        add_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogOkButton))
        add_btn.clicked.connect(self.save_product)

        card_layout.addSpacing(6)
        card_layout.addWidget(add_btn)

        card.setLayout(card_layout)
        main.addWidget(card)
        self.setLayout(main)

    # -------------------------------------------------
    # Load Shops (delegated to controller)
    # -------------------------------------------------
    def load_shops(self):
        shops = self.controller.get_shops()

        for sid, name in shops:
            item = QListWidgetItem()
            checkbox = QCheckBox(name)
            checkbox.setProperty("shop_id", sid)
            self.shop_list.addItem(item)
            self.shop_list.setItemWidget(item, checkbox)

    # -------------------------------------------------
    # Save Product (delegated to controller)
    # -------------------------------------------------
    def save_product(self):
        name = self.name_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Missing Name", "Please enter a product name.")
            return

        # Get selected shops
        selected_shop_ids = []
        for i in range(self.shop_list.count()):
            item = self.shop_list.item(i)
            checkbox = self.shop_list.itemWidget(item)
            if checkbox.isChecked():
                selected_shop_ids.append(checkbox.property("shop_id"))

        self.controller.create_product(name, selected_shop_ids)

        QMessageBox.information(self, "Success", "Product added successfully.")
        self.close()
