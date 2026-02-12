import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog,
    QFrame, QGraphicsDropShadowEffect, QHeaderView
)
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFont, QColor, QPainter, QPen
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

from app.models.sale_details_model import SaleDetailsModel
from app.models.receipt_model import ReceiptModel

class SaleDetailsWindow(QWidget):
    def __init__(self, sale_id):
        super().__init__()
        self.sale_id = sale_id
        self.sale_header = None
        self.sale_items = []

        self.setWindowTitle(f"Sale Details - Invoice #{sale_id}")
        self.resize(900, 520)
        self.setStyleSheet("background: #eef1f6;")

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(16)
        main.setAlignment(Qt.AlignTop)

        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
            }
        """)
        header.setGraphicsEffect(self._shadow())

        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(24, 18, 24, 18)

        self.header_label = QLabel("Loading sale…")
        self.header_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.header_label.setMinimumHeight(36)
        self.header_label.setStyleSheet("color: #222; padding-top: 2px;")
        header_layout.addWidget(self.header_label)

        main.addWidget(header)

        table_card = QFrame()
        table_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
            }
        """)
        table_card.setGraphicsEffect(self._shadow())

        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(16, 16, 16, 16)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Product ID", "Product",
            "Quantity", "Unit Price", "Line Total"
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

        table_layout.addWidget(self.table)
        main.addWidget(table_card, stretch=1)

        summary = QFrame()
        summary.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
            }
        """)
        summary.setGraphicsEffect(self._shadow())

        summary_layout = QVBoxLayout(summary)
        summary_layout.setContentsMargins(24, 18, 24, 18)

        self.summary_label = QLabel("Grand Total: 0.00")
        self.summary_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.summary_label.setStyleSheet("color: #222;")
        summary_layout.addWidget(self.summary_label, alignment=Qt.AlignRight)

        main.addWidget(summary)

        actions = QFrame()
        actions.setStyleSheet("""
            QFrame {
                background: transparent;
            }
        """)
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)

        export_btn = QPushButton("Export Receipt PDF")
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setStyleSheet(self._btn_style("#2d9b5f", "#247f4d"))
        export_btn.clicked.connect(self.export_receipt_pdf)
        actions_layout.addWidget(export_btn)

        print_btn = QPushButton("Print Receipt")
        print_btn.setCursor(Qt.PointingHandCursor)
        print_btn.setStyleSheet(self._btn_style("#4A90E2", "#3b7ac7"))
        print_btn.clicked.connect(self.print_receipt)
        actions_layout.addWidget(print_btn)

        actions_layout.addStretch()
        main.addWidget(actions)

    def load_data(self):
        header = SaleDetailsModel.get_sale_header(self.sale_id)

        if not header:
            QMessageBox.critical(self, "Error", "Sale not found.")
            self.close()
            return

        self.sale_header = header

        # Header
        self.header_label.setText(
            f"Invoice #{header['sale_id']}   |   Shop: {header['shop_name']}   |   Date: {header['date']}"
        )

        # Items
        items = SaleDetailsModel.get_sale_items(self.sale_id)
        self.sale_items = items
        self.table.setRowCount(len(items))

        for r, item in enumerate(items):
            self.table.setItem(r, 0, QTableWidgetItem(str(item["product_id"])))
            self.table.setItem(r, 1, QTableWidgetItem(item["product_name"]))
            self.table.setItem(r, 2, QTableWidgetItem(str(item["quantity"])))
            self.table.setItem(r, 3, QTableWidgetItem(f"{item['price_per_unit']:.2f}"))
            self.table.setItem(r, 4, QTableWidgetItem(f"{item['line_total']:.2f}"))

        # Summary
        self.summary_label.setText(
            f"Grand Total: {header['grand_total']:.2f}"
        )

    def _shadow(self):
        s = QGraphicsDropShadowEffect()
        s.setBlurRadius(16)
        s.setYOffset(3)
        s.setColor(QColor(0, 0, 0, 60))
        return s

    def _btn_style(self, bg, hover):
        return f"""
            QPushButton {{
                background: {bg};
                color: white;
                border-radius: 8px;
                padding: 9px 18px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {hover};
            }}
        """

    def _draw_receipt(self, painter, page_rect):
        header = self.sale_header
        if not header:
            return

        painter.setPen(QPen(Qt.black, 1))
        left = page_rect.left() + 36
        right = page_rect.right() - 36
        width = right - left
        y = page_rect.top() + 36

        # Title
        painter.setFont(QFont("Arial", 16, QFont.Bold))
        title_h = painter.fontMetrics().height()
        painter.drawText(left, y + title_h, "KFC Inventory Receipt")
        y += title_h + 12

        # Meta
        painter.setFont(QFont("Arial", 10))
        meta_h = painter.fontMetrics().height()
        painter.drawText(left, y + meta_h, f"Invoice: #{header['sale_id']}")
        y += meta_h + 6
        painter.drawText(left, y + meta_h, f"Shop: {header['shop_name']}")
        y += meta_h + 6
        painter.drawText(left, y + meta_h, f"Date: {header['date']}")
        y += meta_h + 14

        # Table layout
        col_product = int(width * 0.52)
        col_qty = int(width * 0.12)
        col_price = int(width * 0.18)
        col_total = width - col_product - col_qty - col_price
        x_product = left
        x_qty = x_product + col_product
        x_price = x_qty + col_qty
        x_total = x_price + col_price

        # Header row
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        header_row_h = painter.fontMetrics().height() + 12
        header_rect = QRect(left, y, width, header_row_h)
        product_head_rect = QRect(x_product, y, col_product, header_row_h)
        qty_head_rect = QRect(x_qty, y, col_qty, header_row_h)
        price_head_rect = QRect(x_price, y, col_price, header_row_h)
        total_head_rect = QRect(x_total, y, col_total, header_row_h)

        painter.drawRect(left, y, width, header_row_h)
        painter.drawLine(x_qty, y, x_qty, y + header_row_h)
        painter.drawLine(x_price, y, x_price, y + header_row_h)
        painter.drawLine(x_total, y, x_total, y + header_row_h)
        painter.drawText(product_head_rect.adjusted(6, 0, -6, 0), Qt.AlignVCenter | Qt.AlignLeft, "Product")
        painter.drawText(qty_head_rect.adjusted(6, 0, -6, 0), Qt.AlignVCenter | Qt.AlignRight, "Qty")
        painter.drawText(price_head_rect.adjusted(6, 0, -6, 0), Qt.AlignVCenter | Qt.AlignRight, "Unit Price")
        painter.drawText(total_head_rect.adjusted(6, 0, -6, 0), Qt.AlignVCenter | Qt.AlignRight, "Line Total")
        y += header_row_h

        # Data rows
        painter.setFont(QFont("Arial", 10))
        row_h = painter.fontMetrics().height() + 12
        for item in self.sale_items:
            if y + row_h > page_rect.bottom() - 70:
                # Basic page break for very long receipts
                printer = painter.device()
                if hasattr(printer, "newPage"):
                    printer.newPage()
                y = page_rect.top() + 36
            painter.drawRect(left, y, width, row_h)
            painter.drawLine(x_qty, y, x_qty, y + row_h)
            painter.drawLine(x_price, y, x_price, y + row_h)
            painter.drawLine(x_total, y, x_total, y + row_h)
            product_rect = QRect(x_product, y, col_product, row_h)
            qty_rect = QRect(x_qty, y, col_qty, row_h)
            price_rect = QRect(x_price, y, col_price, row_h)
            total_rect = QRect(x_total, y, col_total, row_h)

            painter.drawText(product_rect.adjusted(6, 0, -6, 0), Qt.AlignVCenter | Qt.AlignLeft, str(item["product_name"]))
            painter.drawText(qty_rect.adjusted(6, 0, -6, 0), Qt.AlignVCenter | Qt.AlignRight, str(item["quantity"]))
            painter.drawText(price_rect.adjusted(6, 0, -6, 0), Qt.AlignVCenter | Qt.AlignRight, f"{item['price_per_unit']:.2f}")
            painter.drawText(total_rect.adjusted(6, 0, -6, 0), Qt.AlignVCenter | Qt.AlignRight, f"{item['line_total']:.2f}")
            y += row_h

        y += 20
        painter.setFont(QFont("Arial", 11, QFont.Bold))
        total_h = painter.fontMetrics().height()
        total_rect = QRect(left, y, width, total_h + 8)
        painter.drawText(
            total_rect.adjusted(0, 0, -6, 0),
            Qt.AlignVCenter | Qt.AlignRight,
            f"Grand Total: {header['grand_total']:.2f}"
        )

    def export_receipt_pdf(self):
        if not self.sale_header:
            QMessageBox.warning(self, "Error", "Sale details are not loaded yet.")
            return

        os.makedirs("receipts", exist_ok=True)
        default_name = f"invoice_{self.sale_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        default_path = os.path.join("receipts", default_name)
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Receipt PDF", default_path, "PDF Files (*.pdf)"
        )
        if not path:
            return

        if not path.lower().endswith(".pdf"):
            path = f"{path}.pdf"

        printer = QPrinter(QPrinter.HighResolution)
        printer.setPaperSize(QPrinter.A4)
        printer.setPageMargins(12, 12, 12, 12, QPrinter.Millimeter)
        printer.setColorMode(QPrinter.Color)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(path)

        try:
            painter = QPainter()
            if not painter.begin(printer):
                raise RuntimeError("Failed to initialize PDF writer")
            self._draw_receipt(painter, printer.pageRect())
            painter.end()
            ReceiptModel.create(self.sale_id, path)
            QMessageBox.information(self, "Export Complete", f"Receipt saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    def print_receipt(self):
        if not self.sale_header:
            QMessageBox.warning(self, "Error", "Sale details are not loaded yet.")
            return

        printer = QPrinter(QPrinter.HighResolution)
        printer.setPaperSize(QPrinter.A4)
        printer.setPageMargins(12, 12, 12, 12, QPrinter.Millimeter)
        printer.setColorMode(QPrinter.Color)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() != QPrintDialog.Accepted:
            return

        try:
            painter = QPainter()
            if not painter.begin(printer):
                raise RuntimeError("Failed to initialize printer")
            self._draw_receipt(painter, printer.pageRect())
            painter.end()
            QMessageBox.information(self, "Printed", "Receipt sent to printer.")
        except Exception as e:
            QMessageBox.critical(self, "Print Failed", str(e))
