# app/views/add_sale_window.py

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from app.controllers.sale_controller import SaleController


class AddSaleWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = SaleController()

        self.setWindowTitle("Add Sale (Invoice)")
        self.resize(820, 520)

        self.setup_ui()
        self.load_shops()

    # -------------------------------------------------
    # UI
    # -------------------------------------------------
    def setup_ui(self):
        main = QVBoxLayout()
        main.setSpacing(10)

        # -------- Title --------
        title = QLabel("New Sale Invoice")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        main.addWidget(title)

        # -------- Shop Selection --------
        top = QHBoxLayout()
        top.addWidget(QLabel("Select Shop:"))

        self.shop_combo = QComboBox()
        self.shop_combo.currentIndexChanged.connect(self.on_shop_changed)
        top.addWidget(self.shop_combo)

        main.addLayout(top)

        # -------- Product Row --------
        prod_row = QHBoxLayout()

        self.product_combo = QComboBox()
        prod_row.addWidget(QLabel("Product:"))
        prod_row.addWidget(self.product_combo, stretch=2)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Sale Price")
        prod_row.addWidget(self.price_input)

        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 1_000_000)
        prod_row.addWidget(QLabel("Qty:"))
        prod_row.addWidget(self.qty_spin)

        add_btn = QPushButton("Add to Cart")
        add_btn.clicked.connect(self.add_to_cart)
        prod_row.addWidget(add_btn)

        main.addLayout(prod_row)

        # -------- Cart Table --------
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Product ID", "Product", "Unit Price",
            "Qty", "Subtotal", "Remove"
        ])
        self.table.setEditTriggers(self.table.NoEditTriggers)
        main.addWidget(self.table, stretch=1)

        # -------- Bottom --------
        bottom = QHBoxLayout()
        self.total_label = QLabel("Total: 0.00")
        self.total_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        bottom.addWidget(self.total_label)

        bottom.addStretch()

        save_btn = QPushButton("Save Sale")
        save_btn.clicked.connect(self.save_sale)
        bottom.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        bottom.addWidget(cancel_btn)

        main.addLayout(bottom)

        self.setLayout(main)

    # -------------------------------------------------
    # Loaders
    # -------------------------------------------------
    def load_shops(self):
        self.shop_combo.clear()
        shops = self.controller.get_shops()

        for s in shops:
            self.shop_combo.addItem(s["shop_name"], s["shop_id"])

        if shops:
            self.shop_combo.setCurrentIndex(0)

    def on_shop_changed(self):
        shop_id = self.shop_combo.currentData()
        self.load_products(shop_id)
        self.clear_cart()

    def load_products(self, shop_id):
        self.product_combo.clear()
        self.products = {}

        if not shop_id:
            return

        rows = self.controller.get_products_for_shop(shop_id)

        for p in rows:
            text = f"{p['product_name']} (Stock: {p['quantity']})"
            self.product_combo.addItem(text, p)
            self.products[p["product_id"]] = p

        if rows:
            self.product_combo.setCurrentIndex(0)

    # -------------------------------------------------
    # Cart
    # -------------------------------------------------
    def add_to_cart(self):
        data = self.product_combo.currentData()
        if not data:
            QMessageBox.warning(self, "Error", "Select a product.")
            return

        try:
            price = float(self.price_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Error", "Enter valid sale price.")
            return

        qty = self.qty_spin.value()

        try:
            self.controller.add_to_cart(
                product_id=data["product_id"],
                name=data["product_name"],
                price=price,
                qty=qty,
                stock=data["quantity"]
            )
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
            return

        self.refresh_table()

    def remove_item(self, index):
        self.controller.remove_from_cart(index)
        self.refresh_table()

    def refresh_table(self):
        cart = self.controller.get_cart()
        self.table.setRowCount(len(cart))

        for r, item in enumerate(cart):
            self.table.setItem(r, 0, QTableWidgetItem(str(item["product_id"])))
            self.table.setItem(r, 1, QTableWidgetItem(item["name"]))
            self.table.setItem(r, 2, QTableWidgetItem(f"{item['price']:.2f}"))
            self.table.setItem(r, 3, QTableWidgetItem(str(item["qty"])))
            self.table.setItem(r, 4, QTableWidgetItem(f"{item['subtotal']:.2f}"))

            btn = QPushButton("Remove")
            btn.clicked.connect(lambda _, i=r: self.remove_item(i))
            self.table.setCellWidget(r, 5, btn)

        self.total_label.setText(f"Total: {self.controller.get_total():.2f}")

    def clear_cart(self):
        self.controller.clear_cart()
        self.refresh_table()

    # -------------------------------------------------
    # Save
    # -------------------------------------------------
    def save_sale(self):
        shop_id = self.shop_combo.currentData()
        if not shop_id:
            QMessageBox.warning(self, "Error", "Select a shop.")
            return

        try:
            sale_id = self.controller.save_sale(shop_id)
            QMessageBox.information(
                self,
                "Success",
                f"Sale saved successfully!\nInvoice #{sale_id}"
            )
            self.close()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save sale:\n{e}")
