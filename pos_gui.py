# pos_gui.py (Windows application)
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from typing import List, Dict

class POSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("StarPlus POS System")
        self.root.geometry("1000x600")
        
        # Initialize database
        self.db_name = "pos_system.db"
        self.init_database()
        
        # Create tabs
        self.tab_control = ttk.Notebook(root)
        
        self.tab_sales = ttk.Frame(self.tab_control)
        self.tab_products = ttk.Frame(self.tab_control)
        self.tab_reports = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab_sales, text='Point of Sale')
        self.tab_control.add(self.tab_products, text='Product Management')
        self.tab_control.add(self.tab_reports, text='Reports')
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Setup each tab
        self.setup_sales_tab()
        self.setup_products_tab()
        self.setup_reports_tab()
        
        # Load initial data
        self.load_products()
        self.load_sales_data()
    
    def init_database(self):
        """Initialize database connection"""
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
    
    def setup_sales_tab(self):
        """Setup the Point of Sale tab"""
        # Left frame for product selection
        left_frame = ttk.LabelFrame(self.tab_sales, text="Products")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Product list
        self.product_tree = ttk.Treeview(left_frame, columns=('id', 'name', 'price', 'stock'), show='headings')
        self.product_tree.heading('id', text='ID')
        self.product_tree.heading('name', text='Name')
        self.product_tree.heading('price', text='Price')
        self.product_tree.heading('stock', text='Stock')
        self.product_tree.column('id', width=50)
        self.product_tree.column('name', width=150)
        self.product_tree.column('price', width=80)
        self.product_tree.column('stock', width=60)
        self.product_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add to cart button
        add_button = ttk.Button(left_frame, text="Add to Cart", command=self.add_to_cart)
        add_button.pack(pady=5)
        
        # Right frame for cart
        right_frame = ttk.LabelFrame(self.tab_sales, text="Shopping Cart")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cart list
        self.cart_tree = ttk.Treeview(right_frame, columns=('id', 'name', 'price', 'quantity', 'total'), show='headings')
        self.cart_tree.heading('id', text='ID')
        self.cart_tree.heading('name', text='Name')
        self.cart_tree.heading('price', text='Price')
        self.cart_tree.heading('quantity', text='Qty')
        self.cart_tree.heading('total', text='Total')
        self.cart_tree.column('id', width=50)
        self.cart_tree.column('name', width=150)
        self.cart_tree.column('price', width=80)
        self.cart_tree.column('quantity', width=50)
        self.cart_tree.column('total', width=80)
        self.cart_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Cart controls
        cart_controls = ttk.Frame(right_frame)
        cart_controls.pack(fill=tk.X, pady=5)
        
        ttk.Button(cart_controls, text="Remove Item", command=self.remove_from_cart).pack(side=tk.LEFT, padx=5)
        ttk.Button(cart_controls, text="Clear Cart", command=self.clear_cart).pack(side=tk.LEFT, padx=5)
        
        # Total label
        self.total_label = ttk.Label(right_frame, text="Total: $0.00", font=('Arial', 14, 'bold'))
        self.total_label.pack(pady=5)
        
        # Checkout button
        checkout_button = ttk.Button(right_frame, text="Process Sale", command=self.process_sale)
        checkout_button.pack(pady=5)
        
        # Initialize cart
        self.cart = []
    
    def setup_products_tab(self):
        """Setup the Product Management tab"""
        # Product list frame
        list_frame = ttk.Frame(self.tab_products)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Product list
        self.product_mgmt_tree = ttk.Treeview(list_frame, columns=('id', 'name', 'price', 'category', 'stock'), show='headings')
        self.product_mgmt_tree.heading('id', text='ID')
        self.product_mgmt_tree.heading('name', text='Name')
        self.product_mgmt_tree.heading('price', text='Price')
        self.product_mgmt_tree.heading('category', text='Category')
        self.product_mgmt_tree.heading('stock', text='Stock')
        self.product_mgmt_tree.column('id', width=50)
        self.product_mgmt_tree.column('name', width=150)
        self.product_mgmt_tree.column('price', width=80)
        self.product_mgmt_tree.column('category', width=100)
        self.product_mgmt_tree.column('stock', width=60)
        self.product_mgmt_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for product list
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.product_mgmt_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.product_mgmt_tree.configure(yscrollcommand=scrollbar.set)
        
        # Product form frame
        form_frame = ttk.LabelFrame(self.tab_products, text="Add/Edit Product")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Form fields
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(form_frame, text="Price:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.price_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.price_var).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(form_frame, text="Category:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.category_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.category_var).grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(form_frame, text="Stock:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.stock_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.stock_var).grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Form buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Add Product", command=self.add_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Product", command=self.update_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Product", command=self.delete_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
    
    def setup_reports_tab(self):
        """Setup the Reports tab"""
        # Report controls frame
        controls_frame = ttk.Frame(self.tab_reports)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(controls_frame, text="Start Date:").pack(side=tk.LEFT, padx=5)
        self.start_date_var = tk.StringVar()
        ttk.Entry(controls_frame, textvariable=self.start_date_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(controls_frame, text="End Date:").pack(side=tk.LEFT, padx=5)
        self.end_date_var = tk.StringVar()
        ttk.Entry(controls_frame, textvariable=self.end_date_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls_frame, text="Generate Report", command=self.generate_report).pack(side=tk.LEFT, padx=5)
        
        # Report display frame
        report_frame = ttk.Frame(self.tab_reports)
        report_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Report text area
        self.report_text = tk.Text(report_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(report_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=scrollbar.set)
        
        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def load_products(self):
        """Load products into the product treeviews"""
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        for item in self.product_mgmt_tree.get_children():
            self.product_mgmt_tree.delete(item)
        
        # Fetch products from database
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY name")
        products = cursor.fetchall()
        
        # Add products to treeviews
        for product in products:
            self.product_tree.insert('', 'end', values=(
                product['id'], product['name'], f"${product['price']:.2f}", product['stock_quantity']
            ))
            
            self.product_mgmt_tree.insert('', 'end', values=(
                product['id'], product['name'], f"${product['price']:.2f}", 
                product['category'], product['stock_quantity']
            ))
    
    def add_to_cart(self):
        """Add selected product to cart"""
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to add to cart")
            return
        
        item = self.product_tree.item(selection[0])
        product_id, name, price_str, stock = item['values']
        price = float(price_str.replace('$', ''))
        stock = int(stock)
        
        # Check if product is already in cart
        for i, cart_item in enumerate(self.cart):
            if cart_item['id'] == product_id:
                # Check stock
                if cart_item['quantity'] >= stock:
                    messagebox.showwarning("Warning", "Not enough stock available")
                    return
                
                # Update quantity
                self.cart[i]['quantity'] += 1
                self.cart[i]['total'] = self.cart[i]['quantity'] * price
                self.update_cart_display()
                return
        
        # Add new item to cart
        if stock < 1:
            messagebox.showwarning("Warning", "Product is out of stock")
            return
        
        self.cart.append({
            'id': product_id,
            'name': name,
            'price': price,
            'quantity': 1,
            'total': price
        })
        
        self.update_cart_display()
    
    def remove_from_cart(self):
        """Remove selected item from cart"""
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove from cart")
            return
        
        index = self.cart_tree.index(selection[0])
        self.cart.pop(index)
        self.update_cart_display()
    
    def clear_cart(self):
        """Clear all items from cart"""
        self.cart = []
        self.update_cart_display()
    
    def update_cart_display(self):
        """Update the cart treeview and total"""
        # Clear cart tree
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Add cart items
        total = 0
        for item in self.cart:
            self.cart_tree.insert('', 'end', values=(
                item['id'], item['name'], f"${item['price']:.2f}", 
                item['quantity'], f"${item['total']:.2f}"
            ))
            total += item['total']
        
        # Update total label
        self.total_label.config(text=f"Total: ${total:.2f}")
    
    def process_sale(self):
        """Process the sale transaction"""
        if not self.cart:
            messagebox.showwarning("Warning", "Cart is empty")
            return
        
        # Confirm sale
        if not messagebox.askyesno("Confirm Sale", "Process this sale?"):
            return
        
        # Prepare sale data
        sale_items = []
        for item in self.cart:
            sale_items.append({
                'product_id': item['id'],
                'quantity': item['quantity']
            })
        
        try:
            # Process sale in database
            cursor = self.conn.cursor()
            transaction_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            for item in sale_items:
                product_id = item['product_id']
                quantity = item['quantity']
                
                # Get product price and stock
                cursor.execute("SELECT price, stock_quantity FROM products WHERE id = ?", (product_id,))
                result = cursor.fetchone()
                if not result:
                    raise Exception(f"Product with ID {product_id} not found")
                
                price, current_stock = result['price'], result['stock_quantity']
                total = price * quantity
                
                # Check stock
                if current_stock < quantity:
                    raise Exception(f"Insufficient stock for product ID {product_id}")
                
                # Update stock
                cursor.execute(
                    "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?",
                    (quantity, product_id)
                )
                
                # Record sale
                cursor.execute(
                    "INSERT INTO sales (transaction_id, product_id, quantity, price, total) VALUES (?, ?, ?, ?, ?)",
                    (transaction_id, product_id, quantity, price, total)
                )
            
            self.conn.commit()
            
            # Show success message
            messagebox.showinfo("Success", f"Sale processed successfully!\nTransaction ID: {transaction_id}")
            
            # Clear cart and reload products
            self.clear_cart()
            self.load_products()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process sale: {str(e)}")
            self.conn.rollback()
    
    def add_product(self):
        """Add a new product"""
        name = self.name_var.get().strip()
        price_str = self.price_var.get().strip()
        category = self.category_var.get().strip()
        stock_str = self.stock_var.get().strip()
        
        if not name or not price_str or not category:
            messagebox.showwarning("Warning", "Please fill in all required fields")
            return
        
        try:
            price = float(price_str)
            stock = int(stock_str) if stock_str else 0
            
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO products (name, price, category, stock_quantity) VALUES (?, ?, ?, ?)",
                (name, price, category, stock)
            )
            self.conn.commit()
            
            messagebox.showinfo("Success", "Product added successfully")
            self.clear_form()
            self.load_products()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for price and stock")
    
    def update_product(self):
        """Update selected product"""
        selection = self.product_mgmt_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to update")
            return
        
        product_id = self.product_mgmt_tree.item(selection[0])['values'][0]
        name = self.name_var.get().strip()
        price_str = self.price_var.get().strip()
        category = self.category_var.get().strip()
        stock_str = self.stock_var.get().strip()
        
        if not name or not price_str or not category:
            messagebox.showwarning("Warning", "Please fill in all required fields")
            return
        
        try:
            price = float(price_str)
            stock = int(stock_str) if stock_str else 0
            
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE products SET name = ?, price = ?, category = ?, stock_quantity = ? WHERE id = ?",
                (name, price, category, stock, product_id)
            )
            self.conn.commit()
            
            messagebox.showinfo("Success", "Product updated successfully")
            self.clear_form()
            self.load_products()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for price and stock")
    
    def delete_product(self):
        """Delete selected product"""
        selection = self.product_mgmt_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to delete")
            return
        
        product_id = self.product_mgmt_tree.item(selection[0])['values'][0]
        product_name = self.product_mgmt_tree.item(selection[0])['values'][1]
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{product_name}'?"):
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Product deleted successfully")
            self.clear_form()
            self.load_products()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Cannot delete product with existing sales records")
    
    def clear_form(self):
        """Clear the product form"""
        self.name_var.set("")
        self.price_var.set("")
        self.category_var.set("")
        self.stock_var.set("")
    
    def load_sales_data(self):
        """Load sales data for reporting"""
        # This would be implemented to fetch sales data from the database
        pass
    
    def generate_report(self):
        """Generate a sales report"""
        start_date = self.start_date_var.get().strip()
        end_date = self.end_date_var.get().strip()
        
        try:
            cursor = self.conn.cursor()
            
            # Build query based on date filters
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
            
            # Generate report text
            report_text = "SALES REPORT\n"
            report_text += "============\n\n"
            
            if start_date or end_date:
                report_text += f"Period: {start_date or 'Start'} to {end_date or 'End'}\n"
            else:
                report_text += "Period: All time\n"
            
            report_text += f"\nTransactions: {result['transactions_count'] or 0}\n"
            report_text += f"Items Sold: {result['items_sold'] or 0}\n"
            report_text += f"Total Revenue: ${result['total_revenue'] or 0:.2f}\n"
            
            # Top products
            report_text += "\nTOP SELLING PRODUCTS\n"
            report_text += "====================\n\n"
            
            top_query = """
                SELECT 
                    p.name,
                    p.category,
                    SUM(s.quantity) as total_sold,
                    SUM(s.total) as total_revenue
                FROM sales s
                JOIN products p ON s.product_id = p.id
            """
            
            top_params = []
            
            if start_date and end_date:
                top_query += " WHERE s.timestamp BETWEEN ? AND ?"
                top_params.extend([start_date, end_date])
            elif start_date:
                top_query += " WHERE s.timestamp >= ?"
                top_params.append(start_date)
            elif end_date:
                top_query += " WHERE s.timestamp <= ?"
                top_params.append(end_date)
            
            top_query += """
                GROUP BY p.id
                ORDER BY total_sold DESC
                LIMIT 10
            """
            
            cursor.execute(top_query, top_params)
            top_products = cursor.fetchall()
            
            for i, product in enumerate(top_products, 1):
                report_text += f"{i}. {product['name']} ({product['category']})\n"
                report_text += f"   Sold: {product['total_sold']} units, Revenue: ${product['total_revenue']:.2f}\n"
            
            # Display report
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(1.0, report_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = POSApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()