# app/views/add_purchase_window.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QSpinBox, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from app.controllers.purchase_controller import PurchaseController


class AddPurchaseWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.controller = PurchaseController()

        self.setWindowTitle("Add Purchase")
        self.setMinimumSize(820, 520)

        self.setup_ui()
        self.load_shops()
        self.load_products()

    # ----------------------------------------------------
    # UI SETUP
    # ----------------------------------------------------
    def setup_ui(self):
        main = QVBoxLayout()

        # --------- TOP ROW ---------
        top = QHBoxLayout()
        top.addWidget(QLabel("Select Shop:"))

        self.shop_combo = QComboBox()
        top.addWidget(self.shop_combo)

        add_row_btn = QPushButton("Add Row")
        add_row_btn.clicked.connect(self.add_row)
        top.addWidget(add_row_btn)

        main.addLayout(top)

        # --------- TABLE ---------
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Product", "Qty", "Price", "Remove"])
        main.addWidget(self.table)

        # --------- BOTTOM ---------
        bottom = QHBoxLayout()

        self.total_label = QLabel("Grand Total: 0.00")
        self.total_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        bottom.addWidget(self.total_label)

        bottom.addStretch()

        save_btn = QPushButton("Save Purchase")
        save_btn.clicked.connect(self.save_purchase)
        bottom.addWidget(save_btn)

        main.addLayout(bottom)
        self.setLayout(main)

    # ----------------------------------------------------
    # LOAD SHOPS / PRODUCTS
    # ----------------------------------------------------
    def load_shops(self):
        shops = self.controller.get_shops()
        self.shop_combo.clear()
        for sid, name in shops:
            self.shop_combo.addItem(name, sid)

    def load_products(self):
        self.products = self.controller.get_products()   # list of tuples
        # Convert to dict for faster lookup
        self.product_dict = {name.lower(): pid for pid, name in self.products}

    # ----------------------------------------------------
    # ADD ROW
    # ----------------------------------------------------
    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # -------- Product dropdown --------
        product_combo = QComboBox()
        product_combo.setEditable(True)

        for pid, name in self.products:
            product_combo.addItem(name, pid)

        product_combo.currentTextChanged.connect(self.recalculate)

        self.table.setCellWidget(row, 0, product_combo)

        # -------- Qty --------
        qty_spin = QSpinBox()
        qty_spin.setRange(1, 100000)
        qty_spin.valueChanged.connect(self.recalculate)
        self.table.setCellWidget(row, 1, qty_spin)

        # -------- Price --------
        price_input = QLineEdit()
        price_input.setPlaceholderText("Enter price")
        price_input.textChanged.connect(self.recalculate)
        self.table.setCellWidget(row, 2, price_input)

        # -------- Remove button --------
        remove_btn = QPushButton("X")
        remove_btn.clicked.connect(lambda _, r=row: self.remove_row(r))
        self.table.setCellWidget(row, 3, remove_btn)

    # ----------------------------------------------------
    def remove_row(self, row):
        self.table.removeRow(row)
        self.recalculate()

    # ----------------------------------------------------
    # Recalculate totals
    # ----------------------------------------------------
    def recalculate(self):
        rows = []
        total = 0

        for r in range(self.table.rowCount()):
            product_combo = self.table.cellWidget(r, 0)
            product_name = product_combo.currentText().strip()

            qty = self.table.cellWidget(r, 1).value()

            price_text = self.table.cellWidget(r, 2).text().strip()
            price = float(price_text) if price_text else 0

            subtotal = qty * price
            total += subtotal

            rows.append({
                "name": product_name,
                "qty": qty,
                "price": price
            })

        self.controller.rows = rows
        self.total_label.setText(f"Grand Total: {total:.2f}")

    # ----------------------------------------------------
    # SAVE PURCHASE
    # ----------------------------------------------------
    def save_purchase(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Error", "Add at least one product row.")
            return

        shop_id = self.shop_combo.currentData()

        try:
            self.controller.save_purchase(shop_id)
            QMessageBox.information(self, "Success", "Purchase saved successfully!")
            self.close()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save purchase:\n{e}")
