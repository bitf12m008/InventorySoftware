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
from app.database_init import DB_PATH

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt

# -------------------------
# Simple DB helpers
# -------------------------
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
    """
    Returns list of dicts: product_id, name, purchase_price, sale_price, quantity
    Only products assigned to the given shop.
    """
    sql = """
    SELECT
      p.product_id,
      p.name as product_name,
      p.purchase_price,
      p.sale_price,
      s.quantity
    FROM Products p
    JOIN Stock s ON p.product_id = s.product_id
    WHERE s.shop_id = ?
    ORDER BY p.name
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, (shop_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

# -------------------------
# Admin Dashboard Widget
# -------------------------
class AdminDashboard(QWidget):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {}
        self.setWindowTitle("Admin Dashboard - Inventory")
        self.resize(900, 600)
        self.setup_ui()
        self.load_shops()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Top row: title + shop selector + actions
        top_layout = QHBoxLayout()
        title = QLabel("Admin Dashboard")
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        top_layout.addWidget(title, stretch=1)

        top_layout.addStretch()

        top_layout.addWidget(QLabel("Select Shop:"))
        self.shop_combo = QComboBox()
        self.shop_combo.currentIndexChanged.connect(self.on_shop_changed)
        top_layout.addWidget(self.shop_combo)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.reload_current_shop)
        top_layout.addWidget(refresh_btn)

        backup_btn = QPushButton("Backup DB")
        backup_btn.clicked.connect(self.backup_db)
        top_layout.addWidget(backup_btn)

        main_layout.addLayout(top_layout)

        # Middle: products table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Product ID", "Product", "Purchase Price", "Sale Price", "Qty"])
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.setSelectionBehavior(self.table.SelectRows)
        main_layout.addWidget(self.table, stretch=1)

        # Bottom: action buttons
        btn_layout = QHBoxLayout()
        add_product_btn = QPushButton("Add Product")
        add_product_btn.clicked.connect(self.add_product)
        btn_layout.addWidget(add_product_btn)

        edit_product_btn = QPushButton("Edit Product")
        edit_product_btn.clicked.connect(self.edit_product)
        btn_layout.addWidget(edit_product_btn)

        adjust_stock_btn = QPushButton("Adjust Stock")
        adjust_stock_btn.clicked.connect(self.adjust_stock)
        btn_layout.addWidget(adjust_stock_btn)

        add_sale_btn = QPushButton("Add Sale")
        add_sale_btn.clicked.connect(self.add_sale)
        btn_layout.addWidget(add_sale_btn)

        reports_btn = QPushButton("Reports")
        reports_btn.clicked.connect(self.open_reports)
        btn_layout.addWidget(reports_btn)

        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    # -------------------------
    # Load / UI handlers
    # -------------------------
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
        QMessageBox.information(self, "Refreshed", "Data refreshed")

    def load_products_for_current_shop(self):
        shop_id = self.shop_combo.currentData()
        if shop_id is None:
            self.table.setRowCount(0)
            return
        rows = fetch_products_with_stock(shop_id)
        self.table.setRowCount(len(rows))
        for r_idx, row in enumerate(rows):
            self.table.setItem(r_idx, 0, QTableWidgetItem(str(row["product_id"])))
            self.table.setItem(r_idx, 1, QTableWidgetItem(row["product_name"]))
            self.table.setItem(r_idx, 2, QTableWidgetItem(f"{row['purchase_price']:.2f}"))
            self.table.setItem(r_idx, 3, QTableWidgetItem(f"{row['sale_price']:.2f}"))
            self.table.setItem(r_idx, 4, QTableWidgetItem(str(row["quantity"])))

    # -------------------------
    # Action placeholders
    # -------------------------
    def add_product(self):
        self.add_product_window = AddProductWindow()
        self.add_product_window.show()

    def edit_product(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Select", "Please select a product to edit.")
            return
        product_id = int(self.table.item(selected, 0).text())
        self.edit_product_window = EditProductWindow(product_id)
        self.edit_product_window.show()


    def adjust_stock(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Select", "Please select a product to adjust stock.")
            return
        product_id = int(self.table.item(selected, 0).text())
        shop_id = self.shop_combo.currentData()
        product_name = self.table.item(selected, 1).text()
        self.adjust_stock_window = AdjustStockWindow(product_id, shop_id, product_name)
        self.adjust_stock_window.show()

    def add_sale(self):
        self.add_sale_window = AddSaleWindow()
        self.add_sale_window.show()

    def open_reports(self):
        # Export current table to CSV as a quick report example
        shop_id = self.shop_combo.currentData()
        shop_name = self.shop_combo.currentText()
        rows = fetch_products_with_stock(shop_id)
        if not rows:
            QMessageBox.information(self, "No Data", "No products to report.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save report as CSV", f"{shop_name}_report.csv", "CSV Files (*.csv)")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["product_id", "product_name", "purchase_price", "sale_price", "quantity"])
            for r in rows:
                writer.writerow([r["product_id"], r["product_name"], r["purchase_price"], r["sale_price"], r["quantity"]])
        QMessageBox.information(self, "Saved", f"Report saved to {path}")

    def backup_db(self):
        # simple backup: copy DB file to user-selected location with timestamp
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"kfc_inventory_backup_{ts}.db"
        path, _ = QFileDialog.getSaveFileName(self, "Save DB Backup", default_name, "SQLite DB (*.db)")
        if not path:
            return
        try:
            from shutil import copyfile
            copyfile(DB_PATH, path)
            QMessageBox.information(self, "Backup", f"Database backed up to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Backup failed: {e}")

# -------------------------
# For quick local test
# -------------------------
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = AdminDashboard()
    w.show()
    sys.exit(app.exec_())
