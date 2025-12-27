from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QDateEdit, QTableWidget, QTableWidgetItem,
    QMessageBox, QFrame, QGraphicsDropShadowEffect, QHeaderView
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont, QColor

from app.models.shop_model import ShopModel
from app.models.profit_report_model import ProfitReportModel

class ProfitReportWindow(QWidget):
    def __init__(self):
        super().__init__()

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
        self.table.setAlternatingRowColors(True)

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.table.setStyleSheet("""
            QTableWidget {
                border: none;
                font-size: 13px;
                alternate-background-color: #f6f8fb;
            }
            QHeaderView::section {
                background: #f0f3f8;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
        """)

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

        report = ProfitReportModel.get_profit_report(
            shop_id, start, end
        )

        if not report:
            self.table.setRowCount(0)
            QMessageBox.information(
                self, "No Data",
                "No sales found for selected period."
            )
            return

        self.table.setRowCount(len(report))

        for row, item in enumerate(report):
            self.table.setItem(row, 0, QTableWidgetItem(str(item["product_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(item["product_name"]))
            self.table.setItem(row, 2, QTableWidgetItem(str(item["qty_sold"])))
            self.table.setItem(row, 3, QTableWidgetItem(f"{item['sale_total']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{item['purchase_cost']:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{item['profit_per_unit']:.2f}"))
            self.table.setItem(row, 6, QTableWidgetItem(f"{item['total_profit']:.2f}"))

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
