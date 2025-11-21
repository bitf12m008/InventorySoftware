# app/adjust_stock_window.py
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QMessageBox
)
import sqlite3
from app.database_init import DB_PATH

class AdjustStockWindow(QWidget):
    def __init__(self, product_id, shop_id, product_name):
        super().__init__()
        self.setWindowTitle("Adjust Stock")
        self.setFixedSize(300, 200)
        self.product_id = product_id
        self.shop_id = shop_id
        self.product_name = product_name

        self.setup_ui()
        self.load_current_quantity()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"Product: {self.product_name}"))

        layout.addWidget(QLabel("Current Quantity:"))
        self.current_qty_label = QLabel("0")
        layout.addWidget(self.current_qty_label)

        layout.addWidget(QLabel("New Quantity:"))
        self.new_qty_input = QLineEdit()
        self.new_qty_input.setPlaceholderText("Enter new quantity")
        layout.addWidget(self.new_qty_input)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_quantity)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def load_current_quantity(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT quantity FROM Stock WHERE product_id = ? AND shop_id = ?", (self.product_id, self.shop_id))
        row = c.fetchone()
        conn.close()
        if row:
            self.current_qty_label.setText(str(row[0]))
            self.new_qty_input.setText(str(row[0]))
        else:
            # If stock row doesn't exist, create one with quantity 0
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO Stock (product_id, shop_id, quantity) VALUES (?, ?, 0)", (self.product_id, self.shop_id))
            conn.commit()
            conn.close()
            self.current_qty_label.setText("0")
            self.new_qty_input.setText("0")

    def save_quantity(self):
        try:
            new_qty = int(self.new_qty_input.text())
            if new_qty < 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "Quantity must be a non-negative integer.")
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE Stock SET quantity = ? WHERE product_id = ? AND shop_id = ?",
                  (new_qty, self.product_id, self.shop_id))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", f"Stock updated to {new_qty}.")
        self.close()
