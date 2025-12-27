from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton,
    QTableWidget, QSpinBox, QLineEdit, QMessageBox, QFrame,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from app.controllers.purchase_controller import PurchaseController

class AddPurchaseWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.controller = PurchaseController()

        self.setWindowTitle("Add Purchase")
        self.setFixedSize(980, 620)
        self.setStyleSheet("background: #eef1f6;")

        self.setup_ui()
        self.load_shops()
        self.load_products()

    def setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(30, 30, 30, 30)
        main.setSpacing(20)
        main.setAlignment(Qt.AlignTop)

        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
            }
        """)

        header_shadow = QGraphicsDropShadowEffect()
        header_shadow.setBlurRadius(18)
        header_shadow.setYOffset(4)
        header_shadow.setColor(QColor(0, 0, 0, 60))
        header.setGraphicsEffect(header_shadow)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 26, 30, 26)

        title = QLabel("Add Purchase")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setMinimumHeight(44)
        title.setStyleSheet("color: #222;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        shop_label = QLabel("Shop")
        shop_label.setFont(QFont("Segoe UI", 11))
        header_layout.addWidget(shop_label)

        self.shop_combo = QComboBox()
        self.shop_combo.setMinimumWidth(220)
        self.shop_combo.setMinimumHeight(40)
        self.shop_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 12px;
                border-radius: 8px;
                border: 1px solid #c9c9c9;
                background: white;
                font-size: 13px;
            }
        """)
        header_layout.addWidget(self.shop_combo)

        add_row_btn = QPushButton("Add Row")
        add_row_btn.setCursor(Qt.PointingHandCursor)
        add_row_btn.setMinimumHeight(40)
        add_row_btn.setStyleSheet("""
            QPushButton {
                background: #4A90E2;
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #3b7ac7;
            }
        """)
        add_row_btn.clicked.connect(self.add_row)
        header_layout.addWidget(add_row_btn)

        main.addWidget(header)

        table_card = QFrame()
        table_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
            }
        """)
        table_card.setGraphicsEffect(header_shadow)

        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(20, 20, 20, 20)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Product", "Quantity", "Price", "Remove"]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: none;
                font-size: 13px;
                alternate-background-color: #f6f8fb;
            }
            QHeaderView::section {
                background: #f0f3f8;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)

        table_layout.addWidget(self.table)
        main.addWidget(table_card, stretch=1)

        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
            }
        """)
        footer.setGraphicsEffect(header_shadow)

        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(30, 24, 30, 24)

        self.total_label = QLabel("Grand Total: 0.00")
        self.total_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.total_label.setStyleSheet("color: #222;")
        footer_layout.addWidget(self.total_label)

        footer_layout.addStretch()

        save_btn = QPushButton("Save Purchase")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setMinimumHeight(46)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #4A90E2;
                color: white;
                border-radius: 10px;
                padding: 10px 24px;
                font-size: 15px;
                font-weight: bold;
                margin-top: 6px;
            }
            QPushButton:hover {
                background: #3b7ac7;
            }
        """)
        save_btn.clicked.connect(self.save_purchase)
        footer_layout.addWidget(save_btn)

        main.addWidget(footer)

    def load_shops(self):
        self.shop_combo.clear()
        for sid, name in self.controller.get_shops():
            self.shop_combo.addItem(name, sid)

    def load_products(self):
        self.products = self.controller.get_products()

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

        product_combo = QComboBox()
        product_combo.setEditable(True)
        product_combo.setMinimumHeight(36)

        for pid, name in self.products:
            product_combo.addItem(name, pid)

        product_combo.currentTextChanged.connect(self.recalculate)
        self.table.setCellWidget(row, 0, product_combo)

        qty_spin = QSpinBox()
        qty_spin.setRange(1, 100000)
        qty_spin.setMinimumHeight(36)
        qty_spin.valueChanged.connect(self.recalculate)
        self.table.setCellWidget(row, 1, qty_spin)

        price_input = QLineEdit()
        price_input.setPlaceholderText("Price")
        price_input.setMinimumHeight(36)
        price_input.textChanged.connect(self.recalculate)
        self.table.setCellWidget(row, 2, price_input)

        remove_btn = QPushButton("✕")
        remove_btn.setCursor(Qt.PointingHandCursor)
        remove_btn.setStyleSheet("""
            QPushButton {
                background: #e04b4b;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #c53e3e;
            }
        """)
        remove_btn.clicked.connect(lambda _, r=row: self.remove_row(r))
        self.table.setCellWidget(row, 3, remove_btn)

    def remove_row(self, row):
        self.table.removeRow(row)
        self.recalculate()

    def recalculate(self):
        rows = []
        total = 0

        for r in range(self.table.rowCount()):
            product_combo = self.table.cellWidget(r, 0)
            qty = self.table.cellWidget(r, 1).value()
            price_text = self.table.cellWidget(r, 2).text().strip()
            price = float(price_text) if price_text else 0

            total += qty * price
            rows.append({
                "name": product_combo.currentText(),
                "qty": qty,
                "price": price
            })

        self.controller.rows = rows
        self.total_label.setText(f"Grand Total: {total:.2f}")

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
