# app/views/profit_report_window.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QDateEdit, QTableWidget, QTableWidgetItem,
    QMessageBox
)
from PyQt5.QtCore import QDate

from app.models.shop_model import ShopModel
from app.models.profit_report_model import ProfitReportModel


class ProfitReportWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Profit Report")
        self.resize(900, 500)

        self.setup_ui()
        self.load_shops()

    # -------------------------------------------------
    # UI SETUP  (unchanged)
    # -------------------------------------------------
    def setup_ui(self):
        layout = QVBoxLayout()

        # ---------------- FILTER BAR ----------------
        filters = QHBoxLayout()

        filters.addWidget(QLabel("Shop:"))
        self.shop_combo = QComboBox()
        filters.addWidget(self.shop_combo)

        filters.addWidget(QLabel("Start Date:"))
        self.start_date = QDateEdit(calendarPopup=True)
        self.start_date.setDate(QDate.currentDate())
        filters.addWidget(self.start_date)

        filters.addWidget(QLabel("End Date:"))
        self.end_date = QDateEdit(calendarPopup=True)
        self.end_date.setDate(QDate.currentDate())
        filters.addWidget(self.end_date)

        load_btn = QPushButton("Load Report")
        load_btn.clicked.connect(self.load_report)
        filters.addWidget(load_btn)

        layout.addLayout(filters)

        # ---------------- TABLE ----------------
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Product ID", "Product", "Qty Sold", "Sale Amount",
            "Purchase Cost", "Profit / Unit", "Total Profit"
        ])
        layout.addWidget(self.table)

        self.setLayout(layout)

    # -------------------------------------------------
    # LOAD SHOPS (via ShopModel)
    # -------------------------------------------------
    def load_shops(self):
        self.shop_combo.clear()

        shops = ShopModel.get_all()   # returns list of rows
        for s in shops:
            self.shop_combo.addItem(s["shop_name"], s["shop_id"])

    # -------------------------------------------------
    # LOAD PROFIT REPORT (via ProfitReportModel)
    # -------------------------------------------------
    def load_report(self):
        shop_id = self.shop_combo.currentData()

        if shop_id is None:
            QMessageBox.warning(self, "Error", "Select a shop")
            return

        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")

        report = ProfitReportModel.get_profit_report(shop_id, start, end)

        if not report:
            self.table.setRowCount(0)
            QMessageBox.information(self, "No Data", "No sales found for selected period.")
            return

        self.table.setRowCount(len(report))

        # Fill table
        for row, item in enumerate(report):
            self.table.setItem(row, 0, QTableWidgetItem(str(item["product_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(item["product_name"]))
            self.table.setItem(row, 2, QTableWidgetItem(str(item["qty_sold"])))
            self.table.setItem(row, 3, QTableWidgetItem(f"{item['sale_total']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{item['purchase_cost']:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{item['profit_per_unit']:.2f}"))
            self.table.setItem(row, 6, QTableWidgetItem(f"{item['total_profit']:.2f}"))
