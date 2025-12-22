from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QDateEdit, QPushButton
)
from PyQt5.QtCore import QDate

from app.models.shop_model import ShopModel
from app.models.sale_model import SaleModel
from app.views.sale_details_window import SaleDetailsWindow


class ShowSalesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sales History")
        self.resize(750, 450)

        self.setup_ui()
        self.load_shops()

    # ---------------- UI ----------------
    def setup_ui(self):
        layout = QVBoxLayout()

        # Filters
        filters = QHBoxLayout()

        filters.addWidget(QLabel("Select Shop:"))
        self.shop_combo = QComboBox()
        self.shop_combo.currentIndexChanged.connect(self.load_sales)
        filters.addWidget(self.shop_combo)

        filters.addWidget(QLabel("Start Date:"))
        self.start_date = QDateEdit(calendarPopup=True)
        self.start_date.setDate(QDate.currentDate())
        filters.addWidget(self.start_date)

        filters.addWidget(QLabel("End Date:"))
        self.end_date = QDateEdit(calendarPopup=True)
        self.end_date.setDate(QDate.currentDate())
        filters.addWidget(self.end_date)

        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load_sales)
        filters.addWidget(load_btn)

        layout.addLayout(filters)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(
            ["Sale ID", "Date", "Total"]
        )
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.open_sale_details)

        layout.addWidget(self.table)
        self.setLayout(layout)

    # ---------------- Data ----------------
    def load_shops(self):
        self.shop_combo.clear()
        shops = ShopModel.get_all()

        for s in shops:
            self.shop_combo.addItem(s["shop_name"], s["shop_id"])

        if shops:
            self.shop_combo.setCurrentIndex(0)
            self.load_sales()

    def load_sales(self):
        shop_id = self.shop_combo.currentData()
        if shop_id is None:
            self.table.setRowCount(0)
            return

        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")

        sales = SaleModel.get_sales_by_shop_and_date(
            shop_id, start, end
        )

        self.table.setRowCount(0)

        if not sales:
            return

        self.table.setRowCount(len(sales))

        for row, sale in enumerate(sales):
            self.table.setItem(row, 0, QTableWidgetItem(str(sale["sale_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(sale["date"]))
            self.table.setItem(row, 2, QTableWidgetItem(f"{sale['grand_total']:.2f}"))

    # ---------------- Actions ----------------
    def open_sale_details(self, row, col):
        sale_id = int(self.table.item(row, 0).text())
        self.details_window = SaleDetailsWindow(sale_id)
        self.details_window.show()
