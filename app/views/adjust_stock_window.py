from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSpinBox,
    QPushButton, QMessageBox, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from app.models.stock_model import StockModel


class AdjustStockWindow(QWidget):
    def __init__(self, product_id, shop_id, product_name):
        super().__init__()

        self.product_id = product_id
        self.shop_id = shop_id

        self.setWindowTitle(f"Adjust Stock – {product_name}")
        self.setMinimumSize(420, 200)
        self.setStyleSheet("background-color: #f5f5f5;")

        self.setup_ui(product_name)

    def setup_ui(self, product_name):
        main = QVBoxLayout()
        main.setContentsMargins(20, 20, 20, 20)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                border: 1px solid #ccc;
            }
        """)
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel(f"Adjust Stock")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)

        subtitle = QLabel(product_name)
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #555; margin-bottom: 10px;")
        card_layout.addWidget(subtitle)

        qty_row = QHBoxLayout()
        qty_row.addWidget(QLabel("New Quantity:"))
        qty_row.addStretch()

        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(0, 10_000_000)
        current_qty = StockModel.get_quantity(self.product_id, self.shop_id)
        self.qty_spin.setValue(current_qty)
        qty_row.addWidget(self.qty_spin)

        card_layout.addLayout(qty_row)

        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                padding: 10px 18px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
        """)
        save_btn.clicked.connect(self.save)

        card_layout.addWidget(save_btn)
        card.setLayout(card_layout)

        main.addWidget(card)
        self.setLayout(main)

    def save(self):
        new_qty = self.qty_spin.value()

        StockModel.set_quantity(
            self.product_id,
            self.shop_id,
            new_qty
        )

        QMessageBox.information(self, "Saved", "Stock updated successfully.")
        self.close()
