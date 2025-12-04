# app/sale_details_window.py

import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt
from app.database_init import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_sale_items(sale_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            si.product_id,
            p.name AS product_name,
            si.quantity,
            si.price_per_unit,
            si.line_total
        FROM SaleItems si
        JOIN Products p ON p.product_id = si.product_id
        WHERE si.sale_id = ?
        ORDER BY p.name
    """, (sale_id,))

    rows = cur.fetchall()
    conn.close()
    return rows


def fetch_sale_header(sale_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT sale_id, shop_id, date, grand_total FROM Sales WHERE sale_id = ?", (sale_id,))
    row = cur.fetchone()
    conn.close()
    return row


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

        self.header_label = QLabel("Loading Sale Info...")
        self.header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.header_label)

        # Table of sale items
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Product ID", "Product", "Qty", "Unit Price", "Line Total"]
        )
        layout.addWidget(self.table)

        # Summary
        self.summary_label = QLabel("Total: 0")
        self.summary_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.summary_label)

        self.setLayout(layout)

    def load_data(self):
        header = fetch_sale_header(self.sale_id)

        if not header:
            QMessageBox.critical(self, "Error", "Sale not found.")
            return

        sale_date = header["date"]
        grand_total = header["grand_total"]

        self.header_label.setText(f"Invoice #{self.sale_id} — Date: {sale_date}")

        # Load items
        rows = fetch_sale_items(self.sale_id)
        self.table.setRowCount(len(rows))

        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(row["product_id"])))
            self.table.setItem(i, 1, QTableWidgetItem(row["product_name"]))
            self.table.setItem(i, 2, QTableWidgetItem(str(row["quantity"])))
            self.table.setItem(i, 3, QTableWidgetItem(f"{row['price_per_unit']:.2f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{row['line_total']:.2f}"))

        self.summary_label.setText(f"Grand Total: {grand_total:.2f}")
