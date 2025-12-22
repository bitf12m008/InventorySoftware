# app/adjust_stock_window.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSpinBox,
    QPushButton, QMessageBox, QHBoxLayout
)
from app.models.stock_model import StockModel

class AdjustStockWindow(QWidget):
    def __init__(self, product_id, shop_id, product_name):
        super().__init__()
        self.product_id = product_id
        self.shop_id = shop_id
        self.setWindowTitle(f"Adjust Stock - {product_name}")
        self.setMinimumSize(360, 140)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Product: {product_name}"))
        row = QHBoxLayout()
        row.addWidget(QLabel("New Quantity:"))
        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(0, 10_000_000)
        current_qty = StockModel.get_quantity(self.product_id, self.shop_id)
        self.qty_spin.setValue(current_qty)

        row.addWidget(self.qty_spin)
        layout.addLayout(row)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def save(self):
        new_qty = self.qty_spin.value()

        StockModel.set_quantity(
            self.product_id,
            self.shop_id,
            new_qty
        )

        QMessageBox.information(self, "Saved", "Stock updated successfully.")
        self.close()
