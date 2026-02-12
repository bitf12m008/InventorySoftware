import csv
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QDateEdit, QTableWidget, QTableWidgetItem,
    QMessageBox, QFrame, QGraphicsDropShadowEffect, QHeaderView, QFileDialog
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont, QColor

from app.models.shop_model import ShopModel
from app.models.profit_report_model import ProfitReportModel

class ProfitReportWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.current_report = []

        self.setWindowTitle("Profit Report")
        self.resize(1000, 560)
        self.setStyleSheet("background: #eef1f6;")

        self.setup_ui()
        self.load_shops()

    def setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(16)
        main.setAlignment(Qt.AlignTop)

        header = self._card()
        h = QHBoxLayout(header)
        h.setContentsMargins(24, 16, 24, 16)

        title = QLabel("Profit Report")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setMinimumHeight(40)
        title.setStyleSheet("color: #222; padding-top: 2px;")
        h.addWidget(title)
        h.addStretch()

        main.addWidget(header)

        filters = self._card()
        f = QHBoxLayout(filters)
        f.setContentsMargins(20, 14, 20, 14)
        f.setSpacing(14)

        f.addWidget(QLabel("Shop"))
        self.shop_combo = QComboBox()
        self.shop_combo.setMinimumWidth(200)
        self.shop_combo.setMinimumHeight(36)
        f.addWidget(self.shop_combo)

        f.addWidget(QLabel("From"))
        self.start_date = QDateEdit(calendarPopup=True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setMinimumWidth(150)
        self.start_date.setMinimumHeight(36)
        f.addWidget(self.start_date)

        f.addWidget(QLabel("To"))
        self.end_date = QDateEdit(calendarPopup=True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setMinimumWidth(150)
        self.end_date.setMinimumHeight(36)
        f.addWidget(self.end_date)

        load_btn = QPushButton("Load Report")
        load_btn.setCursor(Qt.PointingHandCursor)
        load_btn.setStyleSheet("""
            QPushButton {
                background: #4A90E2;
                color: white;
                padding: 6px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #3b7ac7;
            }
        """)
        load_btn.clicked.connect(self.load_report)
        f.addWidget(load_btn)

        export_btn = QPushButton("Export CSV")
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setStyleSheet("""
            QPushButton {
                background: #2d9b5f;
                color: white;
                padding: 6px 20px;
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

        table_card = self._card()
        t = QVBoxLayout(table_card)
        t.setContentsMargins(16, 16, 16, 16)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Product ID", "Product", "Qty Sold",
            "Sale Amount", "Purchase Cost",
            "Profit / Unit", "Total Profit"
        ])
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setSelectionMode(self.table.SingleSelection)
        self.table.setAlternatingRowColors(True)

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

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

        t.addWidget(self.table)
        main.addWidget(table_card, stretch=1)

    def load_shops(self):
        self.shop_combo.clear()
        shops = ShopModel.get_all()
        for s in shops:
            self.shop_combo.addItem(s["shop_name"], s["shop_id"])

    def load_report(self):
        shop_id = self.shop_combo.currentData()
        if shop_id is None:
            QMessageBox.warning(self, "Error", "Select a shop")
            return

        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        if start > end:
            QMessageBox.warning(self, "Invalid Date Range", "From date must be on or before To date.")
            self.table.setRowCount(0)
            self.current_report = []
            return

        report = ProfitReportModel.get_profit_report(
            shop_id, start, end
        )

        if not report:
            self.table.setRowCount(0)
            self.current_report = []
            QMessageBox.information(
                self, "No Data",
                "No sales found for selected period."
            )
            return

        self.current_report = report
        self.table.setRowCount(len(report))

        for row, item in enumerate(report):
            self.table.setItem(row, 0, QTableWidgetItem(str(item["product_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(item["product_name"]))
            qty_item = QTableWidgetItem(str(item["qty_sold"]))
            qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            sale_item = QTableWidgetItem(f"{item['sale_total']:.2f}")
            sale_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            cost_item = QTableWidgetItem(f"{item['purchase_cost']:.2f}")
            cost_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            ppu_item = QTableWidgetItem(f"{item['profit_per_unit']:.2f}")
            ppu_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            profit_item = QTableWidgetItem(f"{item['total_profit']:.2f}")
            profit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 2, qty_item)
            self.table.setItem(row, 3, sale_item)
            self.table.setItem(row, 4, cost_item)
            self.table.setItem(row, 5, ppu_item)
            self.table.setItem(row, 6, profit_item)

    def export_csv(self):
        if not self.current_report:
            QMessageBox.information(self, "No Data", "No report data to export.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Export Profit Report CSV", "profit_report.csv", "CSV Files (*.csv)"
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "product_id", "product_name", "qty_sold", "sale_total",
                    "purchase_cost", "profit_per_unit", "total_profit"
                ])
                for item in self.current_report:
                    writer.writerow([
                        item["product_id"],
                        item["product_name"],
                        item["qty_sold"],
                        f"{item['sale_total']:.2f}",
                        f"{item['purchase_cost']:.2f}",
                        f"{item['profit_per_unit']:.2f}",
                        f"{item['total_profit']:.2f}",
                    ])
            QMessageBox.information(self, "Export Complete", f"Saved CSV to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    def _card(self):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 60))
        frame.setGraphicsEffect(shadow)
        return frame

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
            QComboBox QAbstractItemView {
                background: white;
                color: #222;
                selection-background-color: #808080;
                selection-color: #ffffff;
                outline: 0;
            }
        """
