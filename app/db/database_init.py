import sqlite3
import os
import sys
import hashlib

# EXE-safe base path
def get_base_path():
    if hasattr(sys, "_MEIPASS"):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_DIR = os.path.join(get_base_path(), "database")
DB_PATH = os.path.join(DB_DIR, "app.db")

def initialize_database():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Shops
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Shops (
        shop_id INTEGER PRIMARY KEY AUTOINCREMENT,
        shop_name TEXT NOT NULL
    )
    """)

    # Users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    # Products (master)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)

    # Stock (per shop)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Stock (
        stock_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        shop_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY(product_id) REFERENCES Products(product_id),
        FOREIGN KEY(shop_id) REFERENCES Shops(shop_id)
    )
    """)

    # Sales (invoice header)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Sales (
        sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
        shop_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        grand_total REAL NOT NULL,
        FOREIGN KEY(shop_id) REFERENCES Shops(shop_id)
    )
    """)

    # SaleItems (invoice lines)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS SaleItems (
        sale_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price_per_unit REAL NOT NULL,
        line_total REAL NOT NULL,
        FOREIGN KEY(sale_id) REFERENCES Sales(sale_id),
        FOREIGN KEY(product_id) REFERENCES Products(product_id)
    )
    """)

    # Purchases
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Purchases (
        purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        shop_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        total REAL NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY(product_id) REFERENCES Products(product_id),
        FOREIGN KEY(shop_id) REFERENCES Shops(shop_id)
    )
    """)

    # Receipts (paths for generated receipts)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Receipts (
        receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY(sale_id) REFERENCES Sales(sale_id)
    )
    """)

    conn.commit()

    # default admin
    cursor.execute("SELECT * FROM Users WHERE username='admin'")
    if cursor.fetchone() is None:
        password = "admin123"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("INSERT INTO Users (username, password_hash, role) VALUES (?, ?, ?)",
                       ("admin", password_hash, "admin"))
        conn.commit()

    # default shops
    cursor.execute("SELECT COUNT(*) FROM Shops")
    row = cursor.fetchone()
    if row is None or row[0] == 0:
        default_shops = ["Shop 1", "Shop 2", "Shop 3", "Shop 4"]
        for s in default_shops:
            cursor.execute("INSERT INTO Shops (shop_name) VALUES (?)", (s,))
        conn.commit()

    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    initialize_database()
