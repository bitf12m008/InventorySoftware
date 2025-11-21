from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QMessageBox, QListWidget, QListWidgetItem, QCheckBox
)
from PyQt5.QtCore import Qt
import sqlite3
from app.database_init import DB_PATH

class AddProductWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Product")
        self.setFixedSize(400, 400)

        self.setup_ui()
        self.load_shops()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Product Name
        layout.addWidget(QLabel("Product Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        # Purchase Price
        layout.addWidget(QLabel("Purchase Price:"))
        self.purchase_input = QLineEdit()
        layout.addWidget(self.purchase_input)

        # Sale Price
        layout.addWidget(QLabel("Sale Price:"))
        self.sale_input = QLineEdit()
        layout.addWidget(self.sale_input)

        # Shops list (Checkbox list)
        layout.addWidget(QLabel("Assign Product to Shops:"))
        self.shop_list = QListWidget()
        self.shop_list.setSelectionMode(QListWidget.NoSelection)
        layout.addWidget(self.shop_list)

        # Submit Button
        add_btn = QPushButton("Add Product")
        add_btn.clicked.connect(self.save_product)
        layout.addWidget(add_btn)

        self.setLayout(layout)

    def load_shops(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT shop_id, shop_name FROM Shops")
        shops = c.fetchall()
        conn.close()

        for sid, name in shops:
            item = QListWidgetItem()
            checkbox = QCheckBox(name)
            checkbox.setProperty("shop_id", sid)
            self.shop_list.addItem(item)
            self.shop_list.setItemWidget(item, checkbox)

    def save_product(self):
        name = self.name_input.text()
        purchase = self.purchase_input.text()
        sale = self.sale_input.text()

        if not name or not purchase or not sale:
            QMessageBox.warning(self, "Error", "All fields are required!")
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Add product
        c.execute("""
            INSERT INTO Products (name, purchase_price, sale_price)
            VALUES (?, ?, ?)
        """, (name, float(purchase), float(sale)))

        product_id = c.lastrowid

        # Add stock entries for selected shops
        for i in range(self.shop_list.count()):
            item = self.shop_list.item(i)
            checkbox = self.shop_list.itemWidget(item)
            if checkbox.isChecked():
                shop_id = checkbox.property("shop_id")
                c.execute("""
                    INSERT INTO Stock (product_id, shop_id, quantity)
                    VALUES (?, ?, 0)
                """, (product_id, shop_id))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Product added successfully!")
        self.close()
