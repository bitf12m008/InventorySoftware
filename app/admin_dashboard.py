# app/admin_dashboard.py

import sys
import os
import sqlite3
import csv
import datetime

from app.add_product_window import AddProductWindow
from app.edit_product_window import EditProductWindow
from app.adjust_stock_window import AdjustStockWindow
from app.add_sale_window import AddSaleWindow
from app.add_purchase_window import AddPurchaseWindow
from app.show_sales_window import ShowSalesWindow
from app.profit_report_window import ProfitReportWindow

from app.database_init import DB_PATH

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox,
    QFileDialog, QFrame, QStyle
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


# ---------------------------------------------------
# DB Helpers
# ---------------------------------------------------
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


def fetch_products_with_stock(shop_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.product_id, p.name AS product_name, s.quantity
        FROM Products p
        JOIN Stock s ON p.product_id = s.product_id
        WHERE s.shop_id = ?
        ORDER BY p.name
    """, (shop_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_last_purchase_price(product_id, shop_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT price FROM Purchases
        WHERE product_id=? AND shop_id=?
        ORDER BY purchase_id DESC
        LIMIT 1
    """, (product_id, shop_id))
    row = cur.fetchone()
    conn.close()
    return row["price"] if row else None


def get_avg_purchase_price(product_id, shop_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT SUM(quantity * price) AS total_cost, SUM(quantity) AS total_qty
        FROM Purchases
        WHERE product_id=? AND shop_id=?
    """, (product_id, shop_id))
    row = cur.fetchone()
    conn.close()
    if row and row["total_qty"]:
        return row["total_cost"] / row["total_qty"]
    return None


def get_last_sale_price(product_id, shop_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT si.price_per_unit
        FROM SaleItems si
        JOIN Sales s ON s.sale_id = si.sale_id
        WHERE si.product_id=? AND s.shop_id=?
        ORDER BY si.sale_item_id DESC
        LIMIT 1
    """, (product_id, shop_id))
    row = cur.fetchone()
    conn.close()
    return row["price_per_unit"] if row else None


# ---------------------------------------------------
# Admin Dashboard
# ---------------------------------------------------
class AdminDashboard(QWidget):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {}

        self.setWindowTitle("Admin Dashboard - Inventory")
        self.resize(1250, 700)

        self.setStyleSheet("""
            QWidget {
                background: #f4f4f4;
            }
            QComboBox {
                padding: 6px;
                border: 1px solid #aaa;
                border-radius: 6px;
            }
            QPushButton {
                padding: 8px 14px;
                background: #0078d4;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #005fa3;
            }
            QTableWidget {
                background: white;
                border: 1px solid #ddd;
            }
            QHeaderView::section {
                background: #eaeaea;
                padding: 6px;
                font-weight: bold;
                border: none;
            }
        """)

        self.setup_ui()
        self.load_shops()

    # ---------------------------------------------------
    # UI Setup
    # ---------------------------------------------------
    def setup_ui(self):
        main_layout = QVBoxLayout()

        # ---------------- TOP BAR ----------------
        top_layout = QHBoxLayout()
        title = QLabel("Admin Dashboard")
        title.setFont(QFont("Arial", 18))
        title.setStyleSheet("font-weight: bold; color: #333;")

        top_layout.addWidget(title, stretch=1)
        top_layout.addStretch()

        top_layout.addWidget(QLabel("Select Shop:"))
        self.shop_combo = QComboBox()
        self.shop_combo.currentIndexChanged.connect(self.on_shop_changed)
        top_layout.addWidget(self.shop_combo)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        refresh_btn.clicked.connect(self.reload_current_shop)
        top_layout.addWidget(refresh_btn)

        backup_btn = QPushButton("Backup DB")
        backup_btn.setIcon(self.style().standardIcon(QStyle.SP_DriveHDIcon))
        backup_btn.clicked.connect(self.backup_db)
        top_layout.addWidget(backup_btn)

        main_layout.addLayout(top_layout)

        # ---------------- TABLE ----------------
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Product", "Qty",
            "Avg Cost", "Last Purchase",
            "Last Sale", "Profit"
        ])
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.setSelectionBehavior(self.table.SelectRows)
        main_layout.addWidget(self.table, stretch=1)

        # ---------------- ACTION BUTTONS ----------------
        btn_row = QHBoxLayout()

        def btn(text, icon):
            b = QPushButton(text)
            b.setIcon(self.style().standardIcon(icon))
            return b

        add_product_btn = btn("Add Product", QStyle.SP_FileDialogNewFolder)
        add_product_btn.clicked.connect(self.add_product)
        btn_row.addWidget(add_product_btn)

        edit_product_btn = btn("Edit Product", QStyle.SP_FileDialogContentsView)
        edit_product_btn.clicked.connect(self.edit_product)
        btn_row.addWidget(edit_product_btn)

        adjust_stock_btn = btn("Adjust Stock", QStyle.SP_BrowserReload)
        adjust_stock_btn.clicked.connect(self.adjust_stock)
        btn_row.addWidget(adjust_stock_btn)

        add_purchase_btn = btn("Add Purchase", QStyle.SP_ArrowDown)
        add_purchase_btn.clicked.connect(self.add_purchase)
        btn_row.addWidget(add_purchase_btn)

        add_sale_btn = btn("Add Sale", QStyle.SP_ArrowUp)
        add_sale_btn.clicked.connect(self.add_sale)
        btn_row.addWidget(add_sale_btn)

        show_sales_btn = btn("Show Sales", QStyle.SP_FileIcon)
        show_sales_btn.clicked.connect(self.open_show_sales)
        btn_row.addWidget(show_sales_btn)

        profit_btn = btn("Profit Report", QStyle.SP_ComputerIcon)
        profit_btn.clicked.connect(self.open_profit_report)
        btn_row.addWidget(profit_btn)

        btn_row.addStretch()
        main_layout.addLayout(btn_row)

        self.setLayout(main_layout)

    # ---------------------------------------------------
    # Loaders / Logic
    # ---------------------------------------------------
    def load_shops(self):
        self.shop_combo.clear()
        shops = fetch_shops()

        for s in shops:
            self.shop_combo.addItem(s["shop_name"], s["shop_id"])

        if shops:
            self.shop_combo.setCurrentIndex(0)
            self.load_products_for_current_shop()

    def on_shop_changed(self, idx):
        self.load_products_for_current_shop()

    def reload_current_shop(self):
        self.load_products_for_current_shop()
        QMessageBox.information(self, "Refreshed", "Data refreshed!")

    # ---------------------------------------------------
    # Load Product Table
    # ---------------------------------------------------
    def load_products_for_current_shop(self):
        shop_id = self.shop_combo.currentData()
        if shop_id is None:
            self.table.setRowCount(0)
            return

        products = fetch_products_with_stock(shop_id)

        # Load into table
        self.table.setRowCount(len(products))

        for row, p in enumerate(products):
            pid = p["product_id"]
            qty = p["quantity"]

            avg_cost = get_avg_purchase_price(pid, shop_id)
            last_purchase = get_last_purchase_price(pid, shop_id)
            last_sale = get_last_sale_price(pid, shop_id)

            # Profit color
            if last_purchase is None or last_sale is None:
                profit_text = "N/A"
                color = QColor("gray")
            else:
                diff = last_sale - last_purchase
                profit_text = f"{diff:.2f}"
                color = QColor("green") if diff > 0 else QColor("red")

            # Set rows
            self.table.setItem(row, 0, QTableWidgetItem(str(pid)))
            self.table.setItem(row, 1, QTableWidgetItem(p["product_name"]))
            self.table.setItem(row, 2, QTableWidgetItem(str(qty)))

            self.table.setItem(row, 3, QTableWidgetItem(f"{avg_cost:.2f}" if avg_cost else "-"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{last_purchase:.2f}" if last_purchase else "-"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{last_sale:.2f}" if last_sale else "-"))

            profit_item = QTableWidgetItem(profit_text)
            profit_item.setForeground(color)
            self.table.setItem(row, 6, profit_item)

    # ---------------------------------------------------
    # Button Actions
    # ---------------------------------------------------
    def add_product(self):
        self.add_product_window = AddProductWindow()
        self.add_product_window.show()

    def edit_product(self):
        sel = self.table.currentRow()
        if sel < 0:
            QMessageBox.warning(self, "Select", "Select a product first.")
            return
        pid = int(self.table.item(sel, 0).text())
        self.edit_product_window = EditProductWindow(pid)
        self.edit_product_window.show()

    def adjust_stock(self):
        sel = self.table.currentRow()
        if sel < 0:
            QMessageBox.warning(self, "Select", "Select a product first.")
            return
        pid = int(self.table.item(sel, 0).text())
        shop_id = self.shop_combo.currentData()
        name = self.table.item(sel, 1).text()
        self.adjust_stock_window = AdjustStockWindow(pid, shop_id, name)
        self.adjust_stock_window.show()

    def add_purchase(self):
        self.add_purchase_window = AddPurchaseWindow()
        self.add_purchase_window.show()

    def add_sale(self):
        self.add_sale_window = AddSaleWindow()
        self.add_sale_window.show()

    def open_show_sales(self):
        self.sales_window = ShowSalesWindow()
        self.sales_window.show()

    def open_profit_report(self):
        self.profit_window = ProfitReportWindow()
        self.profit_window.show()

    # ---------------------------------------------------
    # Backup DB
    # ---------------------------------------------------
    def backup_db(self):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default = f"inventory_backup_{ts}.db"
        path, _ = QFileDialog.getSaveFileName(self, "Save Backup", default, "SQLite DB (*.db)")
        if not path:
            return

        try:
            from shutil import copyfile
            copyfile(DB_PATH, path)
            QMessageBox.information(self, "Backup", f"Saved:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# Standalone test
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = AdminDashboard()
    w.show()
    sys.exit(app.exec_())
