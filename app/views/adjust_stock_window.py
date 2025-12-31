from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSpinBox,
    QPushButton, QMessageBox, QHBoxLayout,
    QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from app.models.stock_model import StockModel

class AdjustStockWindow(QWidget):
    def __init__(self, product_id, shop_id, product_name, on_success=None):
        super().__init__()

        self.product_id = product_id
        self.shop_id = shop_id
        self.on_success = on_success

        self.setWindowTitle(f"Adjust Stock – {product_name}")
        self.setFixedSize(460, 320)
        self.setStyleSheet("background: #eef1f6;")

        self.setup_ui(product_name)

    def setup_ui(self, product_name):
        main = QVBoxLayout(self)
        main.setContentsMargins(36, 36, 36, 36)
        main.setAlignment(Qt.AlignTop)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 18px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(22)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 70))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(0)

        title = QLabel("Adjust Stock")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setMinimumHeight(48)
        title.setStyleSheet("""
            color: #222;
            padding-top: 6px;
        """)
        card_layout.addWidget(title)

        card_layout.addSpacing(6)

        subtitle = QLabel(product_name)
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setMinimumHeight(30)
        subtitle.setStyleSheet("color: #666;")
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(24)

        qty_label = QLabel("New Quantity")
        qty_label.setFont(QFont("Segoe UI", 11))
        qty_label.setMinimumHeight(22)
        qty_label.setStyleSheet("color: #444;")

        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(0, 10_000_000)
        self.qty_spin.setMinimumHeight(46)
        self.qty_spin.setMinimumWidth(150)
        self.qty_spin.setFont(QFont("Segoe UI", 11))
        self.qty_spin.setStyleSheet("""
            QSpinBox {
                padding: 8px 12px;
                border-radius: 8px;
                border: 1px solid #c9c9c9;
                background: white;
            }
            QSpinBox:focus {
                border: 1.4px solid #4A90E2;
            }
        """)

        current_qty = StockModel.get_quantity(self.product_id, self.shop_id)
        self.qty_spin.setValue(current_qty)

        qty_row = QHBoxLayout()
        qty_row.addWidget(qty_label)
        qty_row.addStretch()
        qty_row.addWidget(self.qty_spin)

        card_layout.addLayout(qty_row)

        card_layout.addSpacing(24)

        save_btn = QPushButton("Save Changes")
        save_btn.setMinimumHeight(50)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #4A90E2;
                color: white;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 12px;
            }
            QPushButton:hover {
                background: #3b7ac7;
            }
        """)
        save_btn.clicked.connect(self.save)
        card_layout.addWidget(save_btn)

        main.addWidget(card)

    def save(self):
        new_qty = self.qty_spin.value()
        StockModel.set_quantity(self.product_id, self.shop_id, new_qty)
        QMessageBox.information(self, "Saved", "Stock updated successfully.")
        self.on_success()
        self.close()
