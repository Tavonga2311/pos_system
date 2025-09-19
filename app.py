# app.py (Web backend)
from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Database configuration
DATABASE = 'pos_system.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products"""
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return jsonify([dict(product) for product in products])

@app.route('/api/products', methods=['POST'])
def add_product():
    """Add a new product"""
    data = request.get_json()
    required_fields = ['name', 'price', 'category']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO products (name, price, category, stock_quantity) VALUES (?, ?, ?, ?)',
        (data['name'], data['price'], data['category'], data.get('stock_quantity', 0))
    )
    product_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Product added successfully', 'product_id': product_id}), 201

@app.route('/api/sales', methods=['GET'])
def get_sales():
    """Get sales data with optional date filtering"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = '''
        SELECT s.*, p.name as product_name 
        FROM sales s 
        JOIN products p ON s.product_id = p.id
    '''
    params = []
    
    if start_date and end_date:
        query += ' WHERE s.timestamp BETWEEN ? AND ?'
        params.extend([start_date, end_date])
    elif start_date:
        query += ' WHERE s.timestamp >= ?'
        params.append(start_date)
    elif end_date:
        query += ' WHERE s.timestamp <= ?'
        params.append(end_date)
    
    query += ' ORDER BY s.timestamp DESC'
    
    conn = get_db_connection()
    sales = conn.execute(query, params).fetchall()
    conn.close()
    
    return jsonify([dict(sale) for sale in sales])

@app.route('/api/reports/summary', methods=['GET'])
def get_summary_report():
    """Get summary sales report"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = '''
        SELECT 
            COUNT(DISTINCT transaction_id) as transactions_count,
            SUM(quantity) as items_sold,
            SUM(total) as total_revenue
        FROM sales
    '''
    params = []
    
    if start_date and end_date:
        query += ' WHERE timestamp BETWEEN ? AND ?'
        params.extend([start_date, end_date])
    elif start_date:
        query += ' WHERE timestamp >= ?'
        params.append(start_date)
    elif end_date:
        query += ' WHERE timestamp <= ?'
        params.append(end_date)
    
    conn = get_db_connection()
    result = conn.execute(query, params).fetchone()
    conn.close()
    
    report = {
        'transactions_count': result['transactions_count'] or 0,
        'items_sold': result['items_sold'] or 0,
        'total_revenue': result['total_revenue'] or 0.0
    }
    
    return jsonify(report)

@app.route('/api/reports/top-products', methods=['GET'])
def get_top_products():
    """Get top selling products"""
    limit = request.args.get('limit', 10)
    
    query = '''
        SELECT 
            p.id,
            p.name,
            p.category,
            SUM(s.quantity) as total_sold,
            SUM(s.total) as total_revenue
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.id
        ORDER BY total_sold DESC
        LIMIT ?
    '''
    
    conn = get_db_connection()
    products = conn.execute(query, (limit,)).fetchall()
    conn.close()
    
    return jsonify([dict(product) for product in products])

if __name__ == '__main__':
    app.run(debug=True)