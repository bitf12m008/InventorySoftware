# app/profit_report_window.py
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QDateEdit, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from app.db.database_init import DB_PATH


# ----------------------------
# Helper function
# ----------------------------
def get_last_purchase_price(product_id, shop_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT price FROM Purchases
        WHERE product_id = ? AND shop_id = ?
        ORDER BY purchase_id DESC
        LIMIT 1
    """, (product_id, shop_id))
    row = cur.fetchone()
    conn.close()
    if row:
        return float(row[0])
    return 0   # default 0 if never purchased


class ProfitReportWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Profit Report")
        self.resize(900, 500)

        self.setup_ui()
        self.load_shops()

    def setup_ui(self):
        layout = QVBoxLayout()

        # ----------------------------
        # Filters row
        # ----------------------------
        filter_row = QHBoxLayout()

        filter_row.addWidget(QLabel("Shop:"))
        self.shop_combo = QComboBox()
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

        load_btn = QPushButton("Load Report")
        load_btn.clicked.connect(self.load_report)
        filter_row.addWidget(load_btn)

        layout.addLayout(filter_row)

        # ----------------------------
        # Table
        # ----------------------------
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Product ID", "Product", "Qty Sold", "Sale Amount",
            "Purchase Cost", "Profit Per Unit", "Total Profit"
        ])
        layout.addWidget(self.table)

        self.setLayout(layout)

    # ----------------------------
    # Load shops dropdown
    # ----------------------------
    def load_shops(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT shop_id, shop_name FROM Shops")
        rows = cur.fetchall()
        conn.close()

        for shop_id, shop_name in rows:
            self.shop_combo.addItem(shop_name, shop_id)

    # ----------------------------
    # Load report data
    # ----------------------------
    def load_report(self):
        shop_id = self.shop_combo.currentData()
        if shop_id is None:
            QMessageBox.warning(self, "Error", "Please select a shop.")
            return

        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                si.product_id,
                p.name AS product_name,
                si.quantity,
                si.price_per_unit,
                si.line_total
            FROM SaleItems si
            JOIN Sales s ON s.sale_id = si.sale_id
            JOIN Products p ON p.product_id = si.product_id
            WHERE s.shop_id = ?
              AND date(s.date) BETWEEN date(?) AND date(?)
            ORDER BY p.name
        """, (shop_id, start, end))

        sale_items = cur.fetchall()
        conn.close()

        # ----------------------------
        # NEW: Clear table if no sales
        # ----------------------------
        if not sale_items:
            self.table.setRowCount(0)
            QMessageBox.information(self, "No Data", "No sales found for this period.")
            return

        # ----------------------------
        # Calculate report results
        # ----------------------------
        report = {}

        for row in sale_items:
            pid = row["product_id"]
            name = row["product_name"]
            qty = row["quantity"]
            sale_price = row["price_per_unit"]
            sale_total = row["line_total"]

            purchase_price = get_last_purchase_price(pid, shop_id)
            profit_per_unit = sale_price - purchase_price
            total_profit = profit_per_unit * qty
            total_purchase_cost = purchase_price * qty

            if pid not in report:
                report[pid] = {
                    "product_name": name,
                    "qty_sold": 0,
                    "sale_total": 0,
                    "purchase_cost": 0,
                    "profit_per_unit": profit_per_unit,
                    "total_profit": 0
                }

            report[pid]["qty_sold"] += qty
            report[pid]["sale_total"] += sale_total
            report[pid]["purchase_cost"] += total_purchase_cost
            report[pid]["total_profit"] += total_profit

            # ----------------------------
            # Fill table
            # ----------------------------
            self.table.setRowCount(len(report))
        
            for row_idx, (pid, data) in enumerate(report.items()):
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(pid)))
                self.table.setItem(row_idx, 1, QTableWidgetItem(data["product_name"]))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(data["qty_sold"])))
                self.table.setItem(row_idx, 3, QTableWidgetItem(f"{data['sale_total']:.2f}"))
                self.table.setItem(row_idx, 4, QTableWidgetItem(f"{data['purchase_cost']:.2f}"))
                self.table.setItem(row_idx, 5, QTableWidgetItem(f"{data['profit_per_unit']:.2f}"))
                self.table.setItem(row_idx, 6, QTableWidgetItem(f"{data['total_profit']:.2f}"))
