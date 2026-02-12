from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSpinBox,
    QPushButton, QMessageBox, QHBoxLayout,
    QFrame, QGraphicsDropShadowEffect, QToolButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from app.models.stock_model import StockModel
from app.models.audit_log_model import AuditLogModel

class AdjustStockWindow(QWidget):
    def __init__(self, product_id, shop_id, product_name, on_success=None, actor=None):
        super().__init__()

        self.product_id = product_id
        self.shop_id = shop_id
        self.on_success = on_success
        self.actor = actor or {}
        self.product_name = product_name

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
        title.setStyleSheet("color: #222; padding-top: 6px;")
        card_layout.addWidget(title)

        subtitle = QLabel(product_name)
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setMinimumHeight(30)
        subtitle.setStyleSheet("color: #666;")
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(26)

        qty_label = QLabel("New Quantity")
        qty_label.setFont(QFont("Segoe UI", 11))
        qty_label.setStyleSheet("color: #444;")

        qty_container = QFrame()
        qty_container.setFixedHeight(46)
        qty_container.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #c9c9c9;
                border-radius: 8px;
            }
        """)

        qty_layout = QHBoxLayout(qty_container)
        qty_layout.setContentsMargins(10, 4, 10, 4)
        qty_layout.setSpacing(6)

        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(0, 10_000_000)
        self.qty_spin.setFont(QFont("Segoe UI", 11))
        self.qty_spin.setButtonSymbols(QSpinBox.NoButtons)
        self.qty_spin.setStyleSheet("""
            QSpinBox {
                border: none;
                background: transparent;
                font-size: 14px;
            }
        """)

        current_qty = StockModel.get_quantity(self.product_id, self.shop_id)
        self.qty_spin.setValue(current_qty)

        btn_minus = QToolButton()
        btn_minus.setText("−")
        btn_minus.setFont(QFont("Segoe UI", 16, QFont.Bold))
        btn_minus.setCursor(Qt.PointingHandCursor)
        btn_minus.setStyleSheet("""
            QToolButton {
                border: none;
                color: #444;
                padding: 0 6px;
            }
            QToolButton:hover {
                color: #4A90E2;
            }
        """)
        btn_minus.clicked.connect(self.qty_spin.stepDown)

        btn_plus = QToolButton()
        btn_plus.setText("+")
        btn_plus.setFont(QFont("Segoe UI", 15, QFont.Bold))
        btn_plus.setCursor(Qt.PointingHandCursor)
        btn_plus.setStyleSheet("""
            QToolButton {
                border: none;
                color: #444;
                padding: 0 6px;
            }
            QToolButton:hover {
                color: #4A90E2;
            }
        """)
        btn_plus.clicked.connect(self.qty_spin.stepUp)

        qty_layout.addWidget(self.qty_spin)
        qty_layout.addWidget(btn_minus)
        qty_layout.addWidget(btn_plus)

        qty_row = QHBoxLayout()
        qty_row.addWidget(qty_label)
        qty_row.addStretch()
        qty_row.addWidget(qty_container)

        card_layout.addLayout(qty_row)
        card_layout.addSpacing(28)

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
            }
            QPushButton:hover {
                background: #3b7ac7;
            }
        """)
        save_btn.clicked.connect(self.save)
        card_layout.addWidget(save_btn)

        main.addWidget(card)

    def save(self):
        old_qty = StockModel.get_quantity(self.product_id, self.shop_id)
        new_qty = self.qty_spin.value()
        StockModel.set_quantity(self.product_id, self.shop_id, new_qty)
        AuditLogModel.log(
            action="STOCK_ADJUST",
            entity_type="Stock",
            shop_id=self.shop_id,
            product_id=self.product_id,
            user_id=self.actor.get("user_id"),
            username=self.actor.get("username"),
            details=f"{self.product_name}: {old_qty} -> {new_qty}",
        )

        QMessageBox.information(self, "Saved", "Stock updated successfully.")

        if self.on_success:
            self.on_success()

        self.close()
