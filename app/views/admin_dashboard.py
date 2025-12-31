import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox,
    QFrame, QGraphicsDropShadowEffect, QStyle
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from app.controllers.dashboard_controller import DashboardController
from app.views.add_product_window import AddProductWindow
from app.views.edit_product_window import EditProductWindow
from app.views.adjust_stock_window import AdjustStockWindow
from app.views.add_sale_window import AddSaleWindow
from app.views.add_purchase_window import AddPurchaseWindow
from app.views.show_sales_window import ShowSalesWindow
from app.views.profit_report_window import ProfitReportWindow
from app.views.weekly_profit_window import WeeklyProfitWindow
from app.views.staff_management_window import StaffManagementWindow
from app.controllers.backup_controller import BackupController

class AdminDashboard(QWidget):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {}
        self.controller = DashboardController()

        self.setWindowTitle("Admin Dashboard - Inventory")
        self.resize(1300, 760)
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
        header_shadow = QGraphicsDropShadowEffect()
        header_shadow.setBlurRadius(20)
        header_shadow.setYOffset(3)
        header_shadow.setColor(QColor(0, 0, 0, 60))
        header.setGraphicsEffect(header_shadow)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 18, 24, 18)

        title = QLabel("Admin Dashboard")
        title.setFont(QFont("Segoe UI Semibold", 22))
        title.setStyleSheet("color: #222;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        shop_label = QLabel("Shop:")
        shop_label.setFont(QFont("Segoe UI", 11))
        header_layout.addWidget(shop_label)

        self.shop_combo = QComboBox()
        self.shop_combo.setMinimumWidth(220)
        self.shop_combo.currentIndexChanged.connect(self.on_shop_changed)
        self.shop_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border-radius: 8px;
                border: 1px solid #c9c9c9;
                background: white;
                font-size: 13px;
            }
        """)
        header_layout.addWidget(self.shop_combo)

        refresh_btn = self.action_button("Refresh", QStyle.SP_BrowserReload)
        refresh_btn.clicked.connect(self.reload_current_shop)
        header_layout.addWidget(refresh_btn)

        backup_btn = self.action_button("Backup", QStyle.SP_DriveHDIcon)
        backup_btn.clicked.connect(self.backup_db)
        header_layout.addWidget(backup_btn)

        main_layout.addWidget(header)

        table_card = QFrame()
        table_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
            }
        """)
        table_card.setGraphicsEffect(header_shadow)

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
                font-size: 13px;
                background: white;
                alternate-background-color: #f6f8fb;
            }
            QHeaderView::section {
                background: #f0f3f8;
                padding: 10px;
                font-weight: bold;
                border: none;
                color: #333;
            }
        """)

        table_layout.addWidget(self.table)
        main_layout.addWidget(table_card, stretch=1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(14)

        btn_row.addWidget(self.action_button("Add Product", QStyle.SP_FileDialogNewFolder, self.add_product))
        btn_row.addWidget(self.action_button("Edit Product", QStyle.SP_FileDialogContentsView, self.edit_product))
        btn_row.addWidget(self.action_button("Adjust Stock", QStyle.SP_BrowserReload, self.adjust_stock))
        btn_row.addWidget(self.action_button("Add Purchase", QStyle.SP_ArrowDown, self.add_purchase))
        btn_row.addWidget(self.action_button("Add Sale", QStyle.SP_ArrowUp, self.add_sale))
        btn_row.addWidget(self.action_button("Show Sales", QStyle.SP_FileIcon, self.open_show_sales))
        btn_row.addWidget(self.action_button("Profit Report", QStyle.SP_ComputerIcon, self.open_profit_report))
        btn_row.addWidget(self.action_button("Weekly Profit", QStyle.SP_ComputerIcon, self.open_weekly_profit))

        if self.user_info.get("role") == "admin":
           btn_row.addWidget(self.action_button("Staff Management", QStyle.SP_ArrowDown, self.open_staff_management))

        btn_row.addStretch()
        main_layout.addLayout(btn_row)

    def action_button(self, text, icon, slot=None):
        b = QPushButton(text)
        b.setIcon(self.style().standardIcon(icon))
        b.setCursor(Qt.PointingHandCursor)
        b.setMinimumHeight(42)
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

            profit = QTableWidgetItem("N/A" if p["profit"] is None else f"{p['profit']:.2f}")
            if p["profit"] is not None:
                profit.setForeground(QColor("#1a9c4b") if p["profit"] > 0 else QColor("#d64545"))
            self.table.setItem(r, 6, profit)

    def add_product(self):
            self.add_product_window = AddProductWindow(
                on_success=self.reload_current_shop
            )
            self.add_product_window.show()

    def edit_product(self):
        sel = self.table.currentRow()
        if sel < 0:
            QMessageBox.warning(self, "Select", "Select a product first.")
            return
        pid = int(self.table.item(sel, 0).text())
        self.edit_product_window = EditProductWindow(pid, on_success=self.reload_current_shop)
        self.edit_product_window.show()

    def adjust_stock(self):
        sel = self.table.currentRow()
        if sel < 0:
            QMessageBox.warning(self, "Select", "Select a product first.")
            return
        pid = int(self.table.item(sel, 0).text())
        shop_id = self.shop_combo.currentData()
        name = self.table.item(sel, 1).text()
        self.adjust_stock_window = AdjustStockWindow(pid, shop_id, name, on_success=self.reload_current_shop)
        self.adjust_stock_window.show()

    def add_purchase(self):
        self.add_purchase_window = AddPurchaseWindow(on_success=self.reload_current_shop)
        self.add_purchase_window.show()

    def add_sale(self):
        self.add_sale_window = AddSaleWindow(on_success=self.reload_current_shop)
        self.add_sale_window.show()

    def open_show_sales(self):
        self.sales_window = ShowSalesWindow()
        self.sales_window.show()

    def open_profit_report(self):
        self.profit_window = ProfitReportWindow()
        self.profit_window.show()

    def open_weekly_profit(self):
        self.weekly_profit_window = WeeklyProfitWindow()
        self.weekly_profit_window.show()

    def open_staff_management(self):
        self.staff_mgmt = StaffManagementWindow()
        self.staff_mgmt.show()

    def backup_db(self):
        try:
            path = BackupController.backup_forced()
            QMessageBox.information(self, "Backup", f"Backup saved:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = AdminDashboard()
    w.show()
    sys.exit(app.exec_())
