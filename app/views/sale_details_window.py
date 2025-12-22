from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt

from app.models.sale_details_model import SaleDetailsModel


class SaleDetailsWindow(QWidget):
    def __init__(self, sale_id):
        super().__init__()
        self.sale_id = sale_id

        self.setWindowTitle(f"Sale Details - Invoice #{sale_id}")
        self.resize(700, 400)

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.header_label = QLabel("Loading sale...")
        self.header_label.setStyleSheet(
            "font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(self.header_label)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Product ID", "Product", "Qty",
            "Unit Price", "Line Total"
        ])
        self.table.setEditTriggers(self.table.NoEditTriggers)
        layout.addWidget(self.table)

        self.summary_label = QLabel("Grand Total: 0.00")
        self.summary_label.setStyleSheet(
            "font-size: 14px; font-weight: bold;"
        )
        layout.addWidget(self.summary_label)

        self.setLayout(layout)

    def load_data(self):
        header = SaleDetailsModel.get_sale_header(self.sale_id)

        if not header:
            QMessageBox.critical(self, "Error", "Sale not found.")
            self.close()
            return

        self.header_label.setText(
            f"Invoice #{header['sale_id']} — Date: {header['date']}"
        )

        items = SaleDetailsModel.get_sale_items(self.sale_id)

        self.table.setRowCount(len(items))

        for row, item in enumerate(items):
            self.table.setItem(row, 0, QTableWidgetItem(str(item["product_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(item["product_name"]))
            self.table.setItem(row, 2, QTableWidgetItem(str(item["quantity"])))
            self.table.setItem(row, 3, QTableWidgetItem(f"{item['price_per_unit']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{item['line_total']:.2f}"))

        self.summary_label.setText(
            f"Grand Total: {header['grand_total']:.2f}"
        )
