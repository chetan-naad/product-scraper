"""
Database operations using SQLite for Product Price Tracker
"""
import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for price tracking"""

    def __init__(self, db_path: str = "data/products.db"):
        """Initialize database manager with path"""
        self.db_path = db_path
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
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
        logger.info("Database initialized successfully")

    def add_product(self, name, url, alert_price, category, site, currency='INR', current_price=None, image_url=None):
        """Add or reactivate a product with currency and image"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if product exists and is active
        cursor.execute("SELECT id FROM products WHERE product_url = ? AND is_active = 1", (url,))
        if cursor.fetchone():
            conn.close()
            return False

        # Check if product exists but inactive
        cursor.execute("SELECT id FROM products WHERE product_url = ? AND is_active = 0", (url,))
        row = cursor.fetchone()
        if row:
            cursor.execute("""
                UPDATE products 
                SET is_active = 1, product_name = ?, alert_price = ?, category = ?, site = ?, 
                    currency = ?, current_price = ?, image_url = ?, last_updated = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (name, alert_price, category, site, currency, current_price, image_url, row[0]))
            conn.commit()
            conn.close()
            return True

        # Insert new product
        cursor.execute("""
            INSERT INTO products (product_name, product_url, alert_price, category, site, currency, current_price, image_url, is_active, last_updated) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
        """, (name, url, alert_price, category, site, currency, current_price, image_url))
        conn.commit()
        conn.close()
        return True

    def update_price(self, url: str, new_price: float, site: str = "", availability: str = "In Stock") -> Optional[Dict]:
        """Update product price"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, product_name, current_price, alert_price, site
                FROM products WHERE product_url = ?
            """, (url,))

            result = cursor.fetchone()
            if not result:
                conn.close()
                return None

            product_id, name, old_price, alert_price, product_site = result

            price_change = None
            if old_price:
                price_change = ((new_price - old_price) / old_price) * 100

            cursor.execute("""
                UPDATE products 
                SET current_price = ?, last_updated = ?, site = ?
                WHERE product_url = ?
            """, (new_price, datetime.now(), site or product_site, url))

            cursor.execute("""
                INSERT INTO price_history (product_id, price, site, availability)
                VALUES (?, ?, ?, ?)
            """, (product_id, new_price, site or product_site, availability))

            conn.commit()
            conn.close()

            return {
                "product_id": product_id,
                "name": name,
                "old_price": old_price,
                "new_price": new_price,
                "price_change": price_change,
                "alert_price": alert_price,
                "should_alert": new_price <= alert_price if alert_price else False,
                "site": site or product_site
            }
        except Exception as e:
            logger.error(f"Error updating price: {e}")
            return None

    def get_all_products(self) -> List[Dict]:
        """Get all tracked products"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, product_name, product_url, current_price, 
                       alert_price, category, site, currency, image_url, last_updated, is_active
                FROM products
                WHERE is_active = 1
                ORDER BY last_updated DESC
            """)

            products = []
            for row in cursor.fetchall():
                products.append({
                    "id": row[0],
                    "name": row[1],
                    "url": row[2],
                    "current_price": row[3],
                    "alert_price": row[4],
                    "category": row[5],
                    "site": row[6],
                    "currency": row[7],
                    "image_url": row[8],
                    "last_updated": row[9],
                    "is_active": row[10]
                })

            conn.close()
            return products
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            return []

    def get_price_history(self, product_id: int, days: int = 30) -> pd.DataFrame:
        """Get price history"""
        try:
            conn = self.get_connection()
            query = """
                SELECT timestamp, price, site, availability, discount_percentage
                FROM price_history 
                WHERE product_id = ?
                AND timestamp >= datetime('now', '-{} days')
                ORDER BY timestamp
            """.format(days)

            df = pd.read_sql_query(query, conn, params=(product_id,))
            conn.close()

            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except Exception as e:
            logger.error(f"Error getting price history: {e}")
            return pd.DataFrame()

    def get_analytics_data(self) -> Dict:
        """Get analytics data"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM products WHERE is_active = 1")
            total_products = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM products 
                WHERE is_active = 1 AND current_price <= alert_price AND alert_price > 0
            """)
            active_alerts = cursor.fetchone()[0]

            cursor.execute("""
                SELECT AVG(current_price) FROM products 
                WHERE is_active = 1 AND current_price > 0
            """)
            avg_price = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT COUNT(DISTINCT product_id) FROM price_history 
                WHERE date(timestamp) = date('now')
            """)
            price_changes_today = cursor.fetchone()[0]

            cursor.execute("""
                SELECT category, COUNT(*) as count 
                FROM products 
                WHERE is_active = 1 
                GROUP BY category 
                ORDER BY count DESC 
                LIMIT 5
            """)
            top_categories = cursor.fetchall()

            conn.close()

            return {
                "total_products": total_products,
                "active_alerts": active_alerts,
                "avg_price": avg_price,
                "price_changes_today": price_changes_today,
                "top_categories": dict(top_categories)
            }
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {}

    def delete_product(self, product_id: int) -> bool:
        """Delete a product"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            return False

    def export_to_csv(self, csv_path: str = "data/price_export.csv"):
        """Export to CSV"""
        try:
            conn = self.get_connection()
            query = """
                SELECT 
                    p.product_name, p.product_url, p.current_price, p.alert_price,
                    p.category, p.site, p.last_updated,
                    CASE WHEN p.current_price <= p.alert_price AND p.alert_price > 0 
                    THEN 'ALERT' ELSE 'OK' END as status
                FROM products p
                WHERE p.is_active = 1
                ORDER BY p.last_updated DESC
            """
            df = pd.read_sql_query(query, conn)
            df.to_csv(csv_path, index=False)
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error exporting: {e}")
            return False

    def get_best_deals(self, limit: int = 10) -> List[Dict]:
        """Get best deals from multiple sources"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            deals = []
            
            # First, get deals based on price history (products with historical discounts)
            query_history = """
                SELECT 
                    p.id, p.product_name, p.current_price, p.alert_price,
                    p.site, p.category,
                    MAX(ph.price) as max_price,
                    ((MAX(ph.price) - p.current_price) / MAX(ph.price) * 100) as discount_pct
                FROM products p
                JOIN price_history ph ON p.id = ph.product_id
                WHERE p.is_active = 1 AND p.current_price > 0
                GROUP BY p.id
                HAVING discount_pct > 0 AND COUNT(ph.price) > 1
                ORDER BY discount_pct DESC
                LIMIT ?
            """
            cursor.execute(query_history, (limit,))
            history_deals = []
            for row in cursor.fetchall():
                history_deals.append({
                    "id": row[0],
                    "name": row[1],
                    "current_price": row[2],
                    "alert_price": row[3],
                    "site": row[4],
                    "category": row[5],
                    "original_price": row[6],
                    "discount_percent": row[7],
                    "deal_type": "historical_discount"
                })
            
            # Second, get deals based on alert price (products below their alert price)
            query_alert = """
                SELECT 
                    p.id, p.product_name, p.current_price, p.alert_price,
                    p.site, p.category,
                    p.current_price as original_price,
                    ((p.alert_price - p.current_price) / p.alert_price * 100) as discount_pct
                FROM products p
                WHERE p.is_active = 1 AND p.current_price > 0 AND p.alert_price > 0
                AND p.current_price < p.alert_price
                ORDER BY discount_pct DESC
                LIMIT ?
            """
            cursor.execute(query_alert, (limit,))
            alert_deals = []
            for row in cursor.fetchall():
                alert_deals.append({
                    "id": row[0],
                    "name": row[1],
                    "current_price": row[2],
                    "alert_price": row[3],
                    "site": row[4],
                    "category": row[5],
                    "original_price": row[6],
                    "discount_percent": row[7],
                    "deal_type": "below_alert"
                })
            
            # Combine and deduplicate deals (prioritize historical discounts)
            seen_ids = set()
            
            # Add historical deals first
            for deal in history_deals:
                if deal["id"] not in seen_ids:
                    deals.append(deal)
                    seen_ids.add(deal["id"])
            
            # Add alert deals if we haven't reached the limit
            for deal in alert_deals:
                if deal["id"] not in seen_ids and len(deals) < limit:
                    deals.append(deal)
                    seen_ids.add(deal["id"])
            
            # Sort combined deals by discount percentage
            deals.sort(key=lambda x: x["discount_percent"], reverse=True)
            
            conn.close()
            return deals[:limit]
            
        except Exception as e:
            logger.error(f"Error getting deals: {e}")
            return []
