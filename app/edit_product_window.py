# app/edit_product_window.py
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QCheckBox, QMessageBox
)
import sqlite3
from app.database_init import DB_PATH

class EditProductWindow(QWidget):
    def __init__(self, product_id):
        super().__init__()
        self.setWindowTitle("Edit Product")
        self.setFixedSize(400, 450)
        self.product_id = product_id

        self.setup_ui()
        self.load_product()
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
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_product)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def load_product(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name, purchase_price, sale_price FROM Products WHERE product_id = ?", (self.product_id,))
        row = c.fetchone()
        conn.close()
        if row:
            self.name_input.setText(row[0])
            self.purchase_input.setText(str(row[1]))
            self.sale_input.setText(str(row[2]))

    def load_shops(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Get all shops
        c.execute("SELECT shop_id, shop_name FROM Shops")
        shops = c.fetchall()

        # Get shops already assigned to this product
        c.execute("SELECT shop_id FROM Stock WHERE product_id = ?", (self.product_id,))
        assigned_shop_ids = {row[0] for row in c.fetchall()}

        conn.close()

        for shop_id, shop_name in shops:
            item = QListWidgetItem()
            checkbox = QCheckBox(shop_name)
            checkbox.setProperty("shop_id", shop_id)
            if shop_id in assigned_shop_ids:
                checkbox.setChecked(True)
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

        # Update product info
        c.execute("""
            UPDATE Products
            SET name = ?, purchase_price = ?, sale_price = ?
            WHERE product_id = ?
        """, (name, float(purchase), float(sale), self.product_id))

        # Update stock assignments
        # First, get current assignments
        c.execute("SELECT shop_id FROM Stock WHERE product_id = ?", (self.product_id,))
        current_shops = {row[0] for row in c.fetchall()}

        # Get selected shops from UI
        selected_shops = set()
        for i in range(self.shop_list.count()):
            item = self.shop_list.item(i)
            checkbox = self.shop_list.itemWidget(item)
            if checkbox.isChecked():
                selected_shops.add(checkbox.property("shop_id"))

        # Shops to remove
        for shop_id in current_shops - selected_shops:
            c.execute("DELETE FROM Stock WHERE product_id = ? AND shop_id = ?", (self.product_id, shop_id))

        # Shops to add
        for shop_id in selected_shops - current_shops:
            c.execute("INSERT INTO Stock (product_id, shop_id, quantity) VALUES (?, ?, 0)", (self.product_id, shop_id))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Product updated successfully!")
        self.close()
