# app/show_sales_window.py

import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QPushButton
)
from PyQt5.QtCore import Qt, QDate
from app.db.database_init import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_shops():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT shop_id, shop_name FROM Shops ORDER BY shop_name")
    rows = cur.fetchall()
    conn.close()
    return rows


def fetch_sales_for_shop(shop_id, start_date, end_date):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT sale_id, date, grand_total
        FROM Sales
        WHERE shop_id = ?
          AND date(date) BETWEEN date(?) AND date(?)
        ORDER BY sale_id DESC
    """, (shop_id, start_date, end_date))

    rows = cur.fetchall()
    conn.close()
    return rows


class ShowSalesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sales History")
        self.resize(750, 450)

        self.setup_ui()
        self.load_shops()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Top Filters
        filter_row = QHBoxLayout()

        filter_row.addWidget(QLabel("Select Shop:"))
        self.shop_combo = QComboBox()
        self.shop_combo.currentIndexChanged.connect(self.load_sales_for_current_shop)
        filter_row.addWidget(self.shop_combo)

        filter_row.addWidget(QLabel("Start Date:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        filter_row.addWidget(self.start_date)

        filter_row.addWidget(QLabel("End Date:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        filter_row.addWidget(self.end_date)

        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load_sales_for_current_shop)
        filter_row.addWidget(load_btn)

        layout.addLayout(filter_row)

        # Sales Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Sale ID", "Date", "Total"])
        self.table.setEditTriggers(self.table.NoEditTriggers)
        layout.addWidget(self.table)

        # Double-click → details window
        self.table.cellDoubleClicked.connect(self.open_sale_details)

        self.setLayout(layout)

    def load_shops(self):
        self.shop_combo.clear()
        shops = fetch_shops()

        for shop in shops:
            self.shop_combo.addItem(shop["shop_name"], shop["shop_id"])

        if shops:
            self.shop_combo.setCurrentIndex(0)
            self.load_sales_for_current_shop()

    def load_sales_for_current_shop(self):
        shop_id = self.shop_combo.currentData()
        if shop_id is None:
            return

        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")

        sales = fetch_sales_for_shop(shop_id, start, end)

        # Clear table
        self.table.setRowCount(0)

        if not sales:
            return

        self.table.setRowCount(len(sales))

        for i, sale in enumerate(sales):
            self.table.setItem(i, 0, QTableWidgetItem(str(sale["sale_id"])))
            self.table.setItem(i, 1, QTableWidgetItem(sale["date"]))
            self.table.setItem(i, 2, QTableWidgetItem(f"{sale['grand_total']:.2f}"))

    def open_sale_details(self, row, col):
        sale_id = int(self.table.item(row, 0).text())

        from app.sale_details_window import SaleDetailsWindow
        self.details_window = SaleDetailsWindow(sale_id)
        self.details_window.show()
