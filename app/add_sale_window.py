# app/add_sale_window.py
import sqlite3, datetime
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QSpinBox
)
from PyQt5.QtCore import Qt
from app.database_init import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn

def fetch_shops():
    conn = get_connection(); cur = conn.cursor(); cur.execute("SELECT shop_id, shop_name FROM Shops ORDER BY shop_name"); rows = cur.fetchall(); conn.close(); return rows

def fetch_products_for_shop(shop_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""SELECT p.product_id, p.name AS product_name, COALESCE(s.quantity,0) AS stock
                   FROM Products p JOIN Stock s ON p.product_id = s.product_id WHERE s.shop_id = ? ORDER BY p.name""", (shop_id,))
    rows = cur.fetchall(); conn.close(); return rows

class AddSaleWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Sale (Invoice)")
        self.resize(760, 480)
        self.cart = []
        self.setup_ui()
        self.load_shops()

    def setup_ui(self):
        layout = QVBoxLayout()
        top = QHBoxLayout(); top.addWidget(QLabel("Select Shop:"))
        self.shop_combo = QComboBox(); self.shop_combo.currentIndexChanged.connect(self.on_shop_changed); top.addWidget(self.shop_combo)
        layout.addLayout(top)
        prod_row = QHBoxLayout(); prod_row.addWidget(QLabel("Product:"))
        self.product_combo = QComboBox(); prod_row.addWidget(self.product_combo, stretch=2)
        prod_row.addWidget(QLabel("Sale Price:")); self.price_display = QLineEdit(); prod_row.addWidget(self.price_display, stretch=1)
        prod_row.addWidget(QLabel("Qty:")); self.qty_spin = QSpinBox(); self.qty_spin.setRange(1, 1000000); prod_row.addWidget(self.qty_spin)
        add_btn = QPushButton("Add to Cart"); add_btn.clicked.connect(self.on_add_to_cart); prod_row.addWidget(add_btn)
        layout.addLayout(prod_row)
        self.cart_table = QTableWidget(); self.cart_table.setColumnCount(6)
        self.cart_table.setHorizontalHeaderLabels(["Product ID","Product","Unit Price","Qty","Subtotal","Remove"]); self.cart_table.setEditTriggers(self.cart_table.NoEditTriggers)
        layout.addWidget(self.cart_table, stretch=1)
        bottom = QHBoxLayout(); self.total_label = QLabel("Total: 0.00"); bottom.addWidget(self.total_label); bottom.addStretch()
        save_btn = QPushButton("Save Sale"); save_btn.clicked.connect(self.on_save_sale); bottom.addWidget(save_btn)
        cancel_btn = QPushButton("Cancel"); cancel_btn.clicked.connect(self.close); bottom.addWidget(cancel_btn)
        layout.addLayout(bottom)
        self.setLayout(layout)
        self.product_combo.currentIndexChanged.connect(self.on_product_changed)

    def load_shops(self):
        self.shop_combo.clear()
        shops = fetch_shops()
        for s in shops: self.shop_combo.addItem(s["shop_name"], s["shop_id"])
        if shops: self.shop_combo.setCurrentIndex(0)

    def on_shop_changed(self, idx):
        shop_id = self.shop_combo.currentData(); self.load_products(shop_id); self.clear_cart()

    def load_products(self, shop_id):
        self.product_combo.clear()
        if shop_id is None: return
        rows = fetch_products_for_shop(shop_id)
        for r in rows:
            self.product_combo.addItem(f"{r['product_name']} (stock: {r['stock']})",
                                       dict(product_id=r["product_id"], stock=r["stock"], name=r["product_name"]))
        if self.product_combo.count()>0: self.product_combo.setCurrentIndex(0)

    def on_product_changed(self, idx):
        self.price_display.clear(); data=self.product_combo.currentData()
        if data: self.qty_spin.setMaximum(max(1, data["stock"]))

    def on_add_to_cart(self):
        data = self.product_combo.currentData()
        if not data: QMessageBox.warning(self,"No product","Select a product"); return
        try:
            price = float(self.price_display.text().strip())
        except:
            QMessageBox.warning(self,"Price error","Enter valid sale price"); return
        qty = int(self.qty_spin.value()); stock = int(data["stock"])
        if qty > stock: QMessageBox.warning(self,"Stock error",f"Not enough stock (available {stock})"); return
        # combine if exists
        for it in self.cart:
            if it["product_id"]==data["product_id"]:
                new_qty = it["qty"]+qty
                if new_qty>stock: QMessageBox.warning(self,"Stock error",f"Not enough stock (available {stock})"); return
                it["qty"]=new_qty; it["subtotal"]=it["qty"]*it["price"]; self.refresh_cart_table(); self.update_total(); return
        item={"product_id":data["product_id"],"name":data["name"],"price":price,"qty":qty,"subtotal":price*qty,"stock":stock}
        self.cart.append(item); self.refresh_cart_table(); self.update_total()

    def refresh_cart_table(self):
        self.cart_table.setRowCount(len(self.cart))
        for r_idx,item in enumerate(self.cart):
            self.cart_table.setItem(r_idx,0,QTableWidgetItem(str(item["product_id"])))
            self.cart_table.setItem(r_idx,1,QTableWidgetItem(item["name"]))
            self.cart_table.setItem(r_idx,2,QTableWidgetItem(f"{item['price']:.2f}"))
            self.cart_table.setItem(r_idx,3,QTableWidgetItem(str(item["qty"])))
            self.cart_table.setItem(r_idx,4,QTableWidgetItem(f"{item['subtotal']:.2f}"))
            btn=QPushButton("Remove")
            btn.clicked.connect(lambda _,i=r_idx: self.remove_cart_item(i))
            self.cart_table.setCellWidget(r_idx,5,btn)

    def remove_cart_item(self, idx):
        if 0<=idx<len(self.cart): self.cart.pop(idx); self.refresh_cart_table(); self.update_total()

    def update_total(self):
        total = sum(i["subtotal"] for i in self.cart); self.total_label.setText(f"Total: {total:.2f}")

    def clear_cart(self):
        self.cart=[]; self.refresh_cart_table(); self.update_total()

    def on_save_sale(self):
        if not self.cart: QMessageBox.warning(self,"Empty","Add products"); return
        shop_id = self.shop_combo.currentData()
        if shop_id is None: QMessageBox.warning(self,"No shop","Select shop"); return
        conn = get_connection(); cur = conn.cursor()
        # validate stock again
        for item in self.cart:
            cur.execute("SELECT quantity FROM Stock WHERE product_id=? AND shop_id=?", (item["product_id"], shop_id))
            r = cur.fetchone()
            if r is None or item["qty"]>r["quantity"]:
                conn.close(); QMessageBox.critical(self,"Stock error",f"Not enough stock for {item['name']}"); return
        try:
            grand_total = sum(i["subtotal"] for i in self.cart)
            now = datetime.datetime.now().isoformat()
            cur.execute("INSERT INTO Sales (shop_id, date, grand_total) VALUES (?, ?, ?)", (shop_id, now, grand_total))
            sale_id = cur.lastrowid
            for item in self.cart:
                cur.execute("INSERT INTO SaleItems (sale_id, product_id, quantity, price_per_unit, line_total) VALUES (?, ?, ?, ?, ?)",
                            (sale_id, item["product_id"], item["qty"], item["price"], item["subtotal"]))
                cur.execute("UPDATE Stock SET quantity = quantity - ? WHERE product_id = ? AND shop_id = ?",
                            (item["qty"], item["product_id"], shop_id))
            conn.commit(); conn.close()
            QMessageBox.information(self,"Saved",f"Sale saved (Invoice #{sale_id})"); self.clear_cart(); self.load_products(shop_id)
        except Exception as e:
            conn.rollback(); conn.close(); QMessageBox.critical(self,"Error",f"Failed to save sale: {e}")
