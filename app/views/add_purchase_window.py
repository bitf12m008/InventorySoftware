# app/add_purchase_window.py

import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QSpinBox, QLineEdit, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt
from app.models.shop_model import ShopModel
from app.models.product_model import ProductModel
from app.models.stock_model import StockModel
from app.models.purchase_model import PurchaseModel


class AddPurchaseWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Purchase")
        self.setMinimumSize(750, 500)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.load_shops()
        self.load_products()

        self.create_top_section()
        self.create_table()
        self.create_bottom_section()

    # --------------------------
    # Load shops
    # --------------------------
    def load_shops(self):
        self.shops = ShopModel.get_all()

    # --------------------------
    # Load products
    # --------------------------
    def load_products(self):
        self.products = ProductModel.get_all()

    # --------------------------
    # Create top section
    # --------------------------
    def create_top_section(self):
        top = QHBoxLayout()

        top.addWidget(QLabel("Select Shop:"))
        self.shop_dropdown = QComboBox()

        for shop in self.shops:
            self.shop_dropdown.addItem(shop[1], shop[0])

        top.addWidget(self.shop_dropdown)

        add_row_btn = QPushButton("➕ Add Product Row")
        add_row_btn.clicked.connect(self.add_row)
        top.addWidget(add_row_btn)

        self.layout.addLayout(top)

    # --------------------------
    # Create purchase table
    # --------------------------
    def create_table(self):
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Product", "Qty", "Price", "Total", "Remove"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

    # --------------------------
    # Add a row to purchase table
    # --------------------------
    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Editable dropdown for product
        dropdown = QComboBox()
        dropdown.setEditable(True)

        for pid, pname in self.products:
            dropdown.addItem(pname, pid)

        dropdown.currentTextChanged.connect(self.update_totals)
        self.table.setCellWidget(row, 0, dropdown)

        # Qty
        qty = QSpinBox()
        qty.setRange(1, 99999)
        qty.valueChanged.connect(self.update_totals)
        self.table.setCellWidget(row, 1, qty)

        # Price
        price_input = QLineEdit()
        price_input.setPlaceholderText("Enter price")
        price_input.textChanged.connect(self.update_totals)
        self.table.setCellWidget(row, 2, price_input)

        # Total
        total_item = QTableWidgetItem("0")
        total_item.setFlags(total_item.flags() ^ Qt.ItemIsEditable)
        self.table.setItem(row, 3, total_item)

        # Remove button
        remove_btn = QPushButton("❌")
        remove_btn.clicked.connect(lambda _, r=row: self.remove_row(r))
        self.table.setCellWidget(row, 4, remove_btn)

    def remove_row(self, row):
        self.table.removeRow(row)
        self.update_totals()

    # --------------------------
    # UPDATE TOTALS
    # --------------------------
    def update_totals(self):
        for row in range(self.table.rowCount()):
            qty = self.table.cellWidget(row, 1).value()

            price_text = self.table.cellWidget(row, 2).text().strip()
            try:
                price = float(price_text) if price_text else 0
            except:
                price = 0

            total = qty * price
            self.table.item(row, 3).setText(str(total))

        self.update_grand_total()

    def update_grand_total(self):
        total = 0
        for row in range(self.table.rowCount()):
            total += float(self.table.item(row, 3).text())
        self.grand_total_label.setText(f"Grand Total: {total}")

    # --------------------------
    # SAVE PURCHASE
    # --------------------------
    def save_purchase(self):
        shop_id = self.shop_dropdown.currentData()

        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Error", "Add at least one product.")
            return

        for row in range(self.table.rowCount()):
            dropdown = self.table.cellWidget(row, 0)
            typed_name = dropdown.currentText().strip()

            product_id = ProductModel.find_by_name(typed_name)

            if not product_id:
                product_id = ProductModel.create(typed_name)
                StockModel.create(product_id, shop_id, 0)
                self.load_products()

            qty = self.table.cellWidget(row, 1).value()
            price_text = self.table.cellWidget(row, 2).text().strip()

            if not price_text:
                QMessageBox.warning(self, "Error", f"Missing price in row {row+1}.")
                return

            try:
                price = float(price_text)
            except:
                QMessageBox.warning(self, "Error", f"Invalid price in row {row+1}.")
                return

            PurchaseModel.create(product_id, shop_id, qty, price)
            StockModel.increase(product_id, shop_id, qty)

        QMessageBox.information(self, "Success", "Purchase recorded successfully!")
        self.close()

    # --------------------------
    # Bottom Section
    # --------------------------
    def create_bottom_section(self):
        bottom = QHBoxLayout()

        self.grand_total_label = QLabel("Grand Total: 0")
        bottom.addWidget(self.grand_total_label)

        save_btn = QPushButton("Save Purchase")
        save_btn.clicked.connect(self.save_purchase)
        bottom.addWidget(save_btn)

        self.layout.addLayout(bottom)
