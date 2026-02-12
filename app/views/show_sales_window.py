import csv
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QDateEdit, QPushButton,
    QFrame, QGraphicsDropShadowEffect, QHeaderView, QFileDialog, QMessageBox
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont, QColor

from app.models.shop_model import ShopModel
from app.models.sale_model import SaleModel
from app.views.sale_details_window import SaleDetailsWindow


class ShowSalesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.current_sales = []

        self.setWindowTitle("Sales History")
        self.resize(950, 550)
        self.setStyleSheet("background: #eef1f6;")

        self.setup_ui()
        self.load_shops()

    def setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(14)
        main.setAlignment(Qt.AlignTop)

        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
            }
        """)
        header.setGraphicsEffect(self.shadow())

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 16, 24, 16)

        title = QLabel("Sales History")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #222;")
        header_layout.addWidget(title)

        header_layout.addStretch()
        main.addWidget(header)

        filters = QFrame()
        filters.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
            }
        """)
        filters.setGraphicsEffect(self.shadow())

        f = QHBoxLayout(filters)
        f.setContentsMargins(20, 14, 20, 14)
        f.setSpacing(14)

        f.addWidget(QLabel("Shop"))
        self.shop_combo = QComboBox()
        self.shop_combo.setMinimumWidth(180)
        self.shop_combo.currentIndexChanged.connect(self.load_sales)
        self.shop_combo.setMinimumHeight(36)
        f.addWidget(self.shop_combo)

        f.addWidget(QLabel("From"))
        self.start_date = QDateEdit(calendarPopup=True)
        self.start_date.setMinimumWidth(100)
        self.start_date.setMinimumHeight(36)
        self.start_date.setDate(QDate.currentDate())
        f.addWidget(self.start_date)

        f.addWidget(QLabel("To"))
        self.end_date = QDateEdit(calendarPopup=True)
        self.end_date.setMinimumWidth(100)
        self.end_date.setMinimumHeight(36)
        self.end_date.setDate(QDate.currentDate())
        f.addWidget(self.end_date)

        load_btn = QPushButton("Load")
        load_btn.setCursor(Qt.PointingHandCursor)
        load_btn.setStyleSheet("""
            QPushButton {
                background: #4A90E2;
                color: white;
                padding: 6px 18px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #3b7ac7;
            }
        """)
        load_btn.clicked.connect(self.load_sales)
        f.addWidget(load_btn)

        export_btn = QPushButton("Export CSV")
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setStyleSheet("""
            QPushButton {
                background: #2d9b5f;
                color: white;
                padding: 6px 18px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #247f4d;
            }
        """)
        export_btn.clicked.connect(self.export_csv)
        f.addWidget(export_btn)

        f.addStretch()
        main.addWidget(filters)

        table_card = QFrame()
        table_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
            }
        """)
        table_card.setGraphicsEffect(self.shadow())

        t_layout = QVBoxLayout(table_card)
        t_layout.setContentsMargins(16, 16, 16, 16)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Sale ID", "Date", "Total"])
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setSelectionMode(self.table.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.cellDoubleClicked.connect(self.open_sale_details)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

        self.table.setStyleSheet("""
            QTableWidget {
                border: none;
                font-size: 13px;
                alternate-background-color: #f6f8fb;
                selection-background-color: #dbeafe;
                selection-color: #1f2937;
            }
            QHeaderView::section {
                background: #f0f3f8;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
        """)
        self.shop_combo.setStyleSheet(self._control_style())
        self.start_date.setStyleSheet(self._control_style())
        self.end_date.setStyleSheet(self._control_style())

        t_layout.addWidget(self.table)
        main.addWidget(table_card, stretch=1)

    def shadow(self):
        s = QGraphicsDropShadowEffect()
        s.setBlurRadius(16)
        s.setYOffset(3)
        s.setColor(QColor(0, 0, 0, 60))
        return s

    def load_shops(self):
        self.shop_combo.clear()
        shops = ShopModel.get_all()

        for shop_id, shop_name in shops:
            self.shop_combo.addItem(shop_name, shop_id)

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
        if start > end:
            QMessageBox.warning(self, "Invalid Date Range", "From date must be on or before To date.")
            self.table.setRowCount(0)
            self.current_sales = []
            return

        sales = SaleModel.get_sales_by_shop_and_date(shop_id, start, end)
        self.current_sales = sales
        self.table.setRowCount(len(sales))

        for row, sale in enumerate(sales):
            self.table.setItem(row, 0, QTableWidgetItem(str(sale["sale_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(sale["date"]))
            total_item = QTableWidgetItem(f"{sale['grand_total']:.2f}")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 2, total_item)

    def open_sale_details(self, row, col):
        sale_id = int(self.table.item(row, 0).text())
        self.details_window = SaleDetailsWindow(sale_id)
        self.details_window.show()

    def export_csv(self):
        if not self.current_sales:
            QMessageBox.information(self, "No Data", "No sales data to export.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Export Sales CSV", "sales_history.csv", "CSV Files (*.csv)"
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["sale_id", "date", "grand_total"])
                for sale in self.current_sales:
                    writer.writerow([sale["sale_id"], sale["date"], f"{sale['grand_total']:.2f}"])
            QMessageBox.information(self, "Export Complete", f"Saved CSV to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    def _control_style(self):
        return """
            QComboBox, QDateEdit {
                padding: 6px 10px;
                border-radius: 8px;
                border: 1px solid #c9c9c9;
                background: white;
                font-size: 13px;
            }
            QComboBox:focus, QDateEdit:focus {
                border: 1.5px solid #4A90E2;
            }
        """
