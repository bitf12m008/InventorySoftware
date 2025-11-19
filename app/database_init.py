import sqlite3
import os
import sys
import hashlib

def get_base_path():
    if hasattr(sys, "_MEIPASS"):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = get_base_path()
DB_DIR = os.path.join(BASE_DIR, "database")
os.makedirs(DB_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "app.db")

def initialize_database():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ------------------------------
    # Shops
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Shops (
        shop_id INTEGER PRIMARY KEY AUTOINCREMENT,
        shop_name TEXT NOT NULL
    )
    """)

    # ------------------------------
    # Users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL  -- "admin" or "user"
    )
    """)

    # ------------------------------
    # Categories (global)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)

    # ------------------------------
    # ShopCategories (mapping categories to shops)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ShopCategories (
        shop_category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        shop_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        FOREIGN KEY(shop_id) REFERENCES Shops(shop_id),
        FOREIGN KEY(category_id) REFERENCES Categories(category_id)
    )
    """)

    # ------------------------------
    # Products (belong to a category, global)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        purchase_price REAL NOT NULL,
        sale_price REAL NOT NULL,
        FOREIGN KEY(category_id) REFERENCES Categories(category_id)
    )
    """)

    # ------------------------------
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

    # ------------------------------
    # Sales
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Sales (
        sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    # ------------------------------
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

    # ------------------------------
    # Receipts
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

    # ------------------------------
    # Create default admin user if not exists
    cursor.execute("SELECT * FROM Users WHERE username='admin'")
    if cursor.fetchone() is None:
        password = "admin123"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("INSERT INTO Users (username, password_hash, role) VALUES (?, ?, ?)",
                       ("admin", password_hash, "admin"))
        conn.commit()
        print("Default admin user created: username='admin', password='admin123'")

    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    initialize_database()
