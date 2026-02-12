import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog,
    QFrame, QGraphicsDropShadowEffect, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QTextDocument
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

    def _build_receipt_html(self):
        if not self.sale_header:
            return ""

        rows = []
        for item in self.sale_items:
            rows.append(
                f"""
                <tr>
                    <td>{item['product_name']}</td>
                    <td style="text-align:right;">{item['quantity']}</td>
                    <td style="text-align:right;">{item['price_per_unit']:.2f}</td>
                    <td style="text-align:right;">{item['line_total']:.2f}</td>
                </tr>
                """
            )

        rows_html = "\n".join(rows)
        header = self.sale_header
        return f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; font-size: 12px; color: #111; }}
                    h1 {{ font-size: 20px; margin: 0 0 4px 0; }}
                    .meta {{ margin: 0 0 14px 0; color: #444; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
                    th, td {{ border-bottom: 1px solid #ddd; padding: 8px 6px; }}
                    th {{ text-align: left; background: #f5f5f5; }}
                    .total {{ margin-top: 16px; text-align: right; font-size: 15px; font-weight: bold; }}
                </style>
            </head>
            <body>
                <h1>KFC Inventory Receipt</h1>
                <div class="meta">
                    Invoice: #{header['sale_id']}<br/>
                    Shop: {header['shop_name']}<br/>
                    Date: {header['date']}
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th style="text-align:right;">Qty</th>
                            <th style="text-align:right;">Unit Price</th>
                            <th style="text-align:right;">Line Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
                <div class="total">Grand Total: {header['grand_total']:.2f}</div>
            </body>
            </html>
        """

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

        doc = QTextDocument()
        doc.setHtml(self._build_receipt_html())

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(path)

        try:
            doc.print_(printer)
            ReceiptModel.create(self.sale_id, path)
            QMessageBox.information(self, "Export Complete", f"Receipt saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    def print_receipt(self):
        if not self.sale_header:
            QMessageBox.warning(self, "Error", "Sale details are not loaded yet.")
            return

        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() != QPrintDialog.Accepted:
            return

        doc = QTextDocument()
        doc.setHtml(self._build_receipt_html())
        try:
            doc.print_(printer)
            QMessageBox.information(self, "Printed", "Receipt sent to printer.")
        except Exception as e:
            QMessageBox.critical(self, "Print Failed", str(e))
