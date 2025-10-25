import sqlite3
import os

# Delete old database
if os.path.exists('data/products.db'):
    os.remove('data/products.db')
    print("✅ Deleted old database")

# Create new database with correct schema
os.makedirs('data', exist_ok=True)
conn = sqlite3.connect('data/products.db')
cursor = conn.cursor()

# Products table with currency and image_url
cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        product_url TEXT UNIQUE NOT NULL,
        current_price REAL,
        alert_price REAL,
        category TEXT DEFAULT 'Other',
        site TEXT,
        currency TEXT DEFAULT 'INR',
        image_url TEXT,
        last_updated TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
""")

# Price history table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        price REAL NOT NULL,
        site TEXT,
        availability TEXT DEFAULT 'In Stock',
        discount_percentage REAL DEFAULT 0.0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
""")

# Users table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        preferences TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Alerts table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        alert_type TEXT,
        threshold_value REAL,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
""")

conn.commit()
conn.close()
print("✅ Created new database with correct schema!")
print("✅ Ready to run Streamlit")
