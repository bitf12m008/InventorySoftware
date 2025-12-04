# app/edit_product_window.py
import sqlite3
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from app.database_init import DB_PATH

class EditProductWindow(QWidget):
    def __init__(self, product_id):
        super().__init__()
        self.product_id = product_id
        self.setWindowTitle("Edit Product")
        self.setMinimumSize(360, 140)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Product Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        save = QPushButton("Save"); save.clicked.connect(self.save); layout.addWidget(save)
        self.setLayout(layout)
        self.load()

    def load(self):
        conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
        cur.execute("SELECT name FROM Products WHERE product_id=?", (self.product_id,))
        r = cur.fetchone(); conn.close()
        if r: self.name_input.setText(r[0])

    def save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self,"Error","Name required"); return
        conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
        cur.execute("UPDATE Products SET name=? WHERE product_id=?", (name, self.product_id))
        conn.commit(); conn.close()
        QMessageBox.information(self,"Saved","Product updated"); self.close()
