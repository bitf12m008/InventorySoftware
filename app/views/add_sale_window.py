from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QSpinBox,
    QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from app.controllers.sale_controller import SaleController

class AddSaleWindow(QWidget):
    def __init__(self, parent=None, on_success=None, actor=None):
        super().__init__(parent)

        self.controller = SaleController(actor=actor)
        self.on_success=on_success

        self.setWindowTitle("Add Sale (Invoice)")
        self.setFixedSize(1000, 650)
        self.setStyleSheet("background: #eef1f6;")

        self.setup_ui()
        self.load_shops()

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

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 60))
        header.setGraphicsEffect(shadow)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 26, 30, 26)

        title = QLabel("New Sale Invoice")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setMinimumHeight(44)
        title.setStyleSheet("color: #222; padding-top: 4px;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        shop_label = QLabel("Shop")
        shop_label.setFont(QFont("Segoe UI", 11))
        header_layout.addWidget(shop_label)

        self.shop_combo = QComboBox()
        self.shop_combo.setMinimumWidth(220)
        self.shop_combo.setMinimumHeight(40)
        self.shop_combo.currentIndexChanged.connect(self.on_shop_changed)
        self.shop_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 12px;
                border-radius: 8px;
                border: 1px solid #c9c9c9;
                background: white;
                font-size: 13px;
                color: #222;
            }
            QComboBox QAbstractItemView {
                background: white;
                color: #222;
                selection-background-color: #808080;
                selection-color: #ffffff;
                outline: 0;
            }
        """)
        header_layout.addWidget(self.shop_combo)

        main.addWidget(header)

        entry = QFrame()
        entry.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
            }
        """)
        entry.setGraphicsEffect(shadow)

        entry_layout = QHBoxLayout(entry)
        entry_layout.setContentsMargins(30, 24, 30, 24)
        entry_layout.setSpacing(16)

        entry_layout.addWidget(QLabel("Product"))

        self.product_combo = QComboBox()
        self.product_combo.setMinimumHeight(38)
        self.product_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 10px;
                border-radius: 8px;
                border: 1px solid #c9c9c9;
                background: white;
                color: #222;
                font-size: 13px;
            }
            QComboBox:focus {
                border: 1.4px solid #4A90E2;
            }
            QComboBox QAbstractItemView {
                background: white;
                color: #222;
                selection-background-color: #808080;
                selection-color: #ffffff;
                outline: 0;
            }
        """)
        entry_layout.addWidget(self.product_combo, stretch=2)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Sale Price")
        self.price_input.setMinimumHeight(38)
        entry_layout.addWidget(self.price_input)

        entry_layout.addWidget(QLabel("Qty"))

        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 1_000_000)
        self.qty_spin.setMinimumHeight(38)
        entry_layout.addWidget(self.qty_spin)

        add_btn = QPushButton("Add to Cart")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setMinimumHeight(40)
        add_btn.setStyleSheet("""
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
        add_btn.clicked.connect(self.add_to_cart)
        entry_layout.addWidget(add_btn)

        main.addWidget(entry)

        table_card = QFrame()
        table_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
            }
        """)
        table_card.setGraphicsEffect(shadow)

        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(20, 20, 20, 20)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Product ID", "Product", "Unit Price",
            "Quantity", "Subtotal", "Remove"
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(self.table.NoEditTriggers)
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
        footer.setGraphicsEffect(shadow)

        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(30, 24, 30, 24)

        self.total_label = QLabel("Total: 0.00")
        self.total_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.total_label.setStyleSheet("color: #222;")
        footer_layout.addWidget(self.total_label)

        footer_layout.addStretch()

        save_btn = QPushButton("Save Sale")
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
        save_btn.clicked.connect(self.save_sale)
        footer_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setMinimumHeight(46)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #dcdcdc;
                color: #333;
                border-radius: 10px;
                padding: 10px 24px;
                font-size: 14px;
                margin-top: 6px;
            }
            QPushButton:hover {
                background: #cfcfcf;
            }
        """)
        cancel_btn.clicked.connect(self.close)
        footer_layout.addWidget(cancel_btn)

        main.addWidget(footer)

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
            btn.setStyleSheet("""
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
            btn.clicked.connect(lambda _, i=r: self.remove_item(i))
            self.table.setCellWidget(r, 5, btn)

        self.total_label.setText(f"Total: {self.controller.get_total():.2f}")

    def clear_cart(self):
        self.controller.clear_cart()
        self.refresh_table()

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
            if self.on_success:
                self.on_success()
            self.close()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save sale:\n{e}")
