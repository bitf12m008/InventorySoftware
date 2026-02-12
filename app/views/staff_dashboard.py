import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox,
    QFrame, QGraphicsDropShadowEffect, QStyle
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

from app.controllers.dashboard_controller import DashboardController
from app.views.add_sale_window import AddSaleWindow
from app.views.show_sales_window import ShowSalesWindow

class StaffDashboard(QWidget):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {}
        self.controller = DashboardController()

        self.setWindowTitle("Staff Dashboard - Inventory")
        self.showMaximized()
        self.setStyleSheet("background: #eef1f6;")

        self.setup_ui()
        self.load_shops()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 60))
        header.setGraphicsEffect(shadow)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 18, 24, 18)

        title = QLabel("Staff Dashboard")
        title.setFont(QFont("Segoe UI Semibold", 22))
        header_layout.addWidget(title)

        header_layout.addStretch()

        shop_label = QLabel("Shop:")
        shop_label.setFont(QFont("Segoe UI", 11))
        header_layout.addWidget(shop_label)

        self.shop_combo = QComboBox()
        self.shop_combo.setMinimumWidth(220)
        self.shop_combo.setMinimumHeight(40)
        self.shop_combo.setFont(QFont("Segoe UI", 11))
        self.shop_combo.currentIndexChanged.connect(self.on_shop_changed)
        self.shop_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border-radius: 8px;
                border: 1px solid #c9c9c9;
                background: white;
                font-size: 13px;
            }
            QComboBox QAbstractItemView {
                background: white;
                color: #222;
                selection-background-color: #808080;
                selection-color: #ffffff;
                outline: 0;
            }
        """)
        header_layout.addWidget(self.shop_combo)

        refresh_btn = self.action_button("Refresh", QStyle.SP_BrowserReload, self.reload_current_shop)
        header_layout.addWidget(refresh_btn)

        main_layout.addWidget(header)

        table_card = QFrame()
        table_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
            }
        """)
        table_card.setGraphicsEffect(shadow)

        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(20, 20, 20, 20)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Product", "Quantity",
            "Avg Cost", "Last Purchase",
            "Last Sale", "Profit"
        ])
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {
                border: none;
                font-size: 11pt;
                background: white;
                alternate-background-color: #f6f8fb;
            }
            QHeaderView::section {
                background: #f0f3f8;
                padding: 12px;
                font-weight: bold;
                border: none;
                color: #333;
            }
        """)
        self.table.setFont(QFont("Segoe UI", 11))
        self.table.verticalHeader().setDefaultSectionSize(44)

        header_font = QFont("Segoe UI Semibold", 11)
        self.table.horizontalHeader().setFont(header_font)
        self.table.horizontalHeader().setFixedHeight(48)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(
            self.table.horizontalHeader().Stretch
        )

        table_layout.addWidget(self.table)
        main_layout.addWidget(table_card, stretch=1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(14)

        btn_row.addWidget(self.action_button("Add Sale", QStyle.SP_ArrowUp, self.add_sale))
        btn_row.addWidget(self.action_button("Show Sales", QStyle.SP_FileIcon, self.open_show_sales))

        btn_row.addStretch()
        main_layout.addLayout(btn_row)

    def action_button(self, text, icon, slot=None):
        b = QPushButton(text)
        b.setIcon(self.style().standardIcon(icon))
        b.setCursor(Qt.PointingHandCursor)
        b.setMinimumHeight(48)
        b.setFont(QFont("Segoe UI", 11, QFont.Bold))
        b.setStyleSheet("""
            QPushButton {
                background: #4A90E2;
                color: white;
                padding: 10px 16px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #3b7ac7;
            }
        """)
        if slot:
            b.clicked.connect(slot)
        return b

    def load_shops(self):
        self.shop_combo.clear()
        shops = self.controller.get_shops()
        for s in shops:
            self.shop_combo.addItem(s["shop_name"], s["shop_id"])
        if shops:
            self.load_products_for_current_shop()

    def on_shop_changed(self):
        self.load_products_for_current_shop()

    def reload_current_shop(self):
        self.load_products_for_current_shop()
        # QMessageBox.information(self, "Refreshed", "Data refreshed successfully.")

    def load_products_for_current_shop(self):
        shop_id = self.shop_combo.currentData()
        rows = self.controller.get_products_for_shop(shop_id) if shop_id else []
        self.table.setRowCount(len(rows))

        for r, p in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(str(p["product_id"])))
            self.table.setItem(r, 1, QTableWidgetItem(p["product_name"]))
            self.table.setItem(r, 2, QTableWidgetItem(str(p["quantity"])))
            self.table.setItem(r, 3, QTableWidgetItem(f"{p['avg_cost']:.2f}" if p["avg_cost"] else "-"))
            self.table.setItem(r, 4, QTableWidgetItem(f"{p['last_purchase']:.2f}" if p["last_purchase"] else "-"))
            self.table.setItem(r, 5, QTableWidgetItem(f"{p['last_sale']:.2f}" if p["last_sale"] else "-"))

            profit = QTableWidgetItem("-")
            profit.setForeground(QColor("#999"))
            self.table.setItem(r, 6, profit)


    def add_sale(self):
        self.sale_window = AddSaleWindow(
            on_success=self.reload_current_shop,
            actor=self.user_info
        )
        self.sale_window.show()

    def open_show_sales(self):
        self.sales_window = ShowSalesWindow()
        self.sales_window.show()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = StaffDashboard({"username": "staff"})
    w.show()
    sys.exit(app.exec_())
