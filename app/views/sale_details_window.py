from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QMessageBox,
    QFrame, QGraphicsDropShadowEffect, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from app.models.sale_details_model import SaleDetailsModel

class SaleDetailsWindow(QWidget):
    def __init__(self, sale_id):
        super().__init__()
        self.sale_id = sale_id

        self.setWindowTitle(f"Sale Details - Invoice #{sale_id}")
        self.resize(900, 520)
        self.setStyleSheet("background: #eef1f6;")

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(16)
        main.setAlignment(Qt.AlignTop)

        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
            }
        """)
        header.setGraphicsEffect(self._shadow())

        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(24, 18, 24, 18)

        self.header_label = QLabel("Loading sale…")
        self.header_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.header_label.setMinimumHeight(36)
        self.header_label.setStyleSheet("color: #222; padding-top: 2px;")
        header_layout.addWidget(self.header_label)

        main.addWidget(header)

        table_card = QFrame()
        table_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
            }
        """)
        table_card.setGraphicsEffect(self._shadow())

        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(16, 16, 16, 16)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Product ID", "Product",
            "Quantity", "Unit Price", "Line Total"
        ])
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.table.setStyleSheet("""
            QTableWidget {
                border: none;
                font-size: 13px;
                alternate-background-color: #f6f8fb;
            }
            QHeaderView::section {
                background: #f0f3f8;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
        """)

        table_layout.addWidget(self.table)
        main.addWidget(table_card, stretch=1)

        summary = QFrame()
        summary.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
            }
        """)
        summary.setGraphicsEffect(self._shadow())

        summary_layout = QVBoxLayout(summary)
        summary_layout.setContentsMargins(24, 18, 24, 18)

        self.summary_label = QLabel("Grand Total: 0.00")
        self.summary_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.summary_label.setStyleSheet("color: #222;")
        summary_layout.addWidget(self.summary_label, alignment=Qt.AlignRight)

        main.addWidget(summary)

    def load_data(self):
        header = SaleDetailsModel.get_sale_header(self.sale_id)

        if not header:
            QMessageBox.critical(self, "Error", "Sale not found.")
            self.close()
            return

        # Header
        self.header_label.setText(
            f"Invoice #{header['sale_id']}   |   Date: {header['date']}"
        )

        # Items
        items = SaleDetailsModel.get_sale_items(self.sale_id)
        self.table.setRowCount(len(items))

        for r, item in enumerate(items):
            self.table.setItem(r, 0, QTableWidgetItem(str(item["product_id"])))
            self.table.setItem(r, 1, QTableWidgetItem(item["product_name"]))
            self.table.setItem(r, 2, QTableWidgetItem(str(item["quantity"])))
            self.table.setItem(r, 3, QTableWidgetItem(f"{item['price_per_unit']:.2f}"))
            self.table.setItem(r, 4, QTableWidgetItem(f"{item['line_total']:.2f}"))

        # Summary
        self.summary_label.setText(
            f"Grand Total: {header['grand_total']:.2f}"
        )

    def _shadow(self):
        s = QGraphicsDropShadowEffect()
        s.setBlurRadius(16)
        s.setYOffset(3)
        s.setColor(QColor(0, 0, 0, 60))
        return s
