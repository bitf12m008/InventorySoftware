# app/adjust_stock_window.py
import sqlite3
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpinBox, QPushButton, QMessageBox, QHBoxLayout
from app.db.database_init import DB_PATH

class AdjustStockWindow(QWidget):
    def __init__(self, product_id, shop_id, product_name):
        super().__init__()
        self.product_id = product_id
        self.shop_id = shop_id
        self.setWindowTitle(f"Adjust stock - {product_name}")
        self.setMinimumSize(360, 140)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Product: {product_name}"))
        row = QHBoxLayout()
        row.addWidget(QLabel("New Quantity:"))
        self.qty_spin = QSpinBox(); self.qty_spin.setRange(0, 10000000)
        # load current
        conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
        cur.execute("SELECT quantity FROM Stock WHERE product_id=? AND shop_id=?", (self.product_id, self.shop_id))
        r = cur.fetchone()
        conn.close()
        if r: self.qty_spin.setValue(r[0])
        row.addWidget(self.qty_spin)
        layout.addLayout(row)
        save = QPushButton("Save"); save.clicked.connect(self.save); layout.addWidget(save)
        self.setLayout(layout)

    def save(self):
        new_q = self.qty_spin.value()
        conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
        cur.execute("UPDATE Stock SET quantity=? WHERE product_id=? AND shop_id=?", (new_q, self.product_id, self.shop_id))
        if cur.rowcount == 0:
            cur.execute("INSERT INTO Stock (product_id, shop_id, quantity) VALUES (?, ?, ?)", (self.product_id, self.shop_id, new_q))
        conn.commit(); conn.close()
        QMessageBox.information(self,"Saved","Stock updated"); self.close()
