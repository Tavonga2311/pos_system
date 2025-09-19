# pos_system.py
import sqlite3
import json
import datetime
from typing import List, Dict, Optional

class POSSystem:
    """A simple Point of Sale system with local database and cloud sync capability"""
    
    def __init__(self, db_name="pos_system.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT,
                stock_quantity INTEGER DEFAULT 0
            )
        ''')
        
        # Sales table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                total REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                synced INTEGER DEFAULT 0,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Sync log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT NOT NULL,
                sync_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL
            )
        ''')
        
        # Insert some sample products if none exist
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            sample_products = [
                ("Laptop", 999.99, "Electronics", 10),
                ("Mouse", 24.99, "Electronics", 50),
                ("Keyboard", 49.99, "Electronics", 30),
                ("Monitor", 199.99, "Electronics", 15),
                ("Desk", 149.99, "Furniture", 8),
                ("Chair", 89.99, "Furniture", 12)
            ]
            cursor.executemany(
                "INSERT INTO products (name, price, category, stock_quantity) VALUES (?, ?, ?, ?)",
                sample_products
            )
        
        conn.commit()
        conn.close()
    
    def add_product(self, name: str, price: float, category: str, stock_quantity: int = 0) -> int:
        """Add a new product to the database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, price, category, stock_quantity) VALUES (?, ?, ?, ?)",
            (name, price, category, stock_quantity)
        )
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return product_id
    
    def get_products(self) -> List[Dict]:
        """Retrieve all products from the database"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return products
    
    def process_sale(self, items: List[Dict]) -> str:
        """Process a sale transaction"""
        transaction_id = f"TXN{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        for item in items:
            product_id = item['product_id']
            quantity = item['quantity']
            
            # Get product price
            cursor.execute("SELECT price, stock_quantity FROM products WHERE id = ?", (product_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Product with ID {product_id} not found")
            
            price, current_stock = result
            total = price * quantity
            
            # Update stock
            if current_stock < quantity:
                raise ValueError(f"Insufficient stock for product ID {product_id}")
            
            cursor.execute(
                "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?",
                (quantity, product_id)
            )
            
            # Record sale
            cursor.execute(
                "INSERT INTO sales (transaction_id, product_id, quantity, price, total) VALUES (?, ?, ?, ?, ?)",
                (transaction_id, product_id, quantity, price, total)
            )
        
        conn.commit()
        conn.close()
        return transaction_id
    
    def get_unsynced_sales(self) -> List[Dict]:
        """Retrieve sales that haven't been synced to the cloud"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.*, p.name as product_name 
            FROM sales s 
            JOIN products p ON s.product_id = p.id 
            WHERE s.synced = 0
        """)
        sales = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return sales
    
    def mark_as_synced(self, transaction_id: str) -> bool:
        """Mark a transaction as synced to the cloud"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE sales SET synced = 1 WHERE transaction_id = ?",
            (transaction_id,)
        )
        cursor.execute(
            "INSERT INTO sync_log (transaction_id, status) VALUES (?, ?)",
            (transaction_id, "success")
        )
        conn.commit()
        conn.close()
        return True
    
    def get_sales_report(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """Generate a sales report for the given period"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        query = """
            SELECT 
                COUNT(DISTINCT transaction_id) as transactions_count,
                SUM(quantity) as items_sold,
                SUM(total) as total_revenue
            FROM sales
        """
        params = []
        
        if start_date and end_date:
            query += " WHERE timestamp BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        elif start_date:
            query += " WHERE timestamp >= ?"
            params.append(start_date)
        elif end_date:
            query += " WHERE timestamp <= ?"
            params.append(end_date)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        
        report = {
            "transactions_count": result[0] or 0,
            "items_sold": result[1] or 0,
            "total_revenue": result[2] or 0.0
        }
        
        conn.close()
        return report

# Cloud sync functionality (simulated)
class CloudSync:
    """Simulated cloud synchronization service"""
    
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
    
    def upload_sales_data(self, sales_data: List[Dict]) -> bool:
        """Simulate uploading sales data to the cloud"""
        print(f"Uploading {len(sales_data)} sales records to {self.api_url}")
        print(f"Using API key: {self.api_key}")
        print("Data:", json.dumps(sales_data, indent=2))
        
        # In a real implementation, this would make an HTTP request
        # For now, we'll just simulate a successful upload
        return True

# Example usage
if __name__ == "__main__":
    # Initialize the POS system
    pos = POSSystem()
    
    # Display available products
    print("Available Products:")
    for product in pos.get_products():
        print(f"{product['id']}: {product['name']} - ${product['price']} (Stock: {product['stock_quantity']})")
    
    # Process a sample sale
    sample_sale = [
        {"product_id": 1, "quantity": 1},  # 1 Laptop
        {"product_id": 2, "quantity": 2}   # 2 Mice
    ]
    
    try:
        transaction_id = pos.process_sale(sample_sale)
        print(f"\nSale processed successfully! Transaction ID: {transaction_id}")
    except Exception as e:
        print(f"Error processing sale: {e}")
    
    # Get unsynced sales
    unsynced_sales = pos.get_unsynced_sales()
    print(f"\nUnsynced sales: {len(unsynced_sales)}")
    
    # Simulate cloud sync
    if unsynced_sales:
        cloud_sync = CloudSync("https://api.example.com/pos/sync", "your_api_key_here")
        if cloud_sync.upload_sales_data(unsynced_sales):
            # Mark as synced if upload was successful
            for sale in unsynced_sales:
                pos.mark_as_synced(sale['transaction_id'])
            print("Sales data successfully synced to cloud!")
    
    # Generate a sales report
    report = pos.get_sales_report()
    print("\nSales Report:")
    print(f"Transactions: {report['transactions_count']}")
    print(f"Items Sold: {report['items_sold']}")
    print(f"Total Revenue: ${report['total_revenue']:.2f}")