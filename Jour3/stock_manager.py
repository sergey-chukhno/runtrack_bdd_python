import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from datetime import datetime
from PIL import Image, ImageTk
import os
from dotenv import load_dotenv

load_dotenv()

class StockManager:
    def __init__(self):
        self.setup_database()
        self.setup_gui()
        
    def setup_database(self):
    
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password=os.getenv("DB_PASSWORD")
            )
            cursor = self.conn.cursor()
            
            cursor.execute("CREATE DATABASE IF NOT EXISTS Store")
            cursor.execute("USE Store")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS category (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    price INT,
                    quantity INT,
                    id_category INT,
                    FOREIGN KEY (id_category) REFERENCES category(id)
                )
            """)
            cursor.execute("SELECT COUNT(*) FROM category")
            if cursor.fetchone()[0] == 0:
                categories = ["Electronics", "Clothing", "Food", "Books"]
                for cat in categories:
                    cursor.execute("INSERT INTO category (name) VALUES (%s)", (cat,))
            
            cursor.execute("SELECT COUNT(*) FROM product")
            if cursor.fetchone()[0] == 0:
                sample_products = [
                    ("Laptop", "High-performance laptop", 999, 10, 1),
                    ("T-shirt", "Cotton t-shirt", 20, 100, 2),
                    ("Chocolate", "Dark chocolate bar", 5, 200, 3),
                    ("Python Book", "Programming guide", 45, 50, 4)
                ]
                cursor.execute("SELECT id FROM category")
                categories = cursor.fetchall()
                for i, prod in enumerate(sample_products):
                    cursor.execute("""
                        INSERT INTO product (name, description, price, quantity, id_category)
                        VALUES (%s, %s, %s, %s, %s)
                    """, prod)
            
            self.conn.commit()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            
    def setup_gui(self):
        self.root = ctk.CTk()
        self.root.title("Stock Manager Pro")
        self.root.geometry("1400x900")
        ctk.set_appearance_mode("light")
        
        self.colors = {
            'primary': '#2563eb', 
            'secondary': '#3b82f6', 
            'accent': '#1d4ed8',  
            'success': '#059669',  
            'warning': '#d97706', 
            'danger': '#dc2626', 
            'background': '#f8fafc', 
            'text': '#1e293b',
            'kpi_blue': '#3b82f6',
            'kpi_amber': '#f59e0b',
            'kpi_green': '#10b981',
            'kpi_red': '#ef4444'
        }
    
        self.fonts = {
            'heading': ('Helvetica', 24, 'bold'),
            'subheading': ('Helvetica', 18, 'bold'),
            'body': ('Helvetica', 12),
            'small': ('Helvetica', 10),
            'kpi_value': ('Helvetica', 28, 'bold'),
            'kpi_title': ('Helvetica', 14)
        }
        
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Treeview",
                       background="#ffffff",
                       foreground=self.colors['text'],
                       rowheight=30,
                       fieldbackground="#ffffff",
                       bordercolor=self.colors['primary'],
                       borderwidth=0)
        style.configure("Treeview.Heading",
                       background=self.colors['primary'],
                       foreground="white",
                       relief="flat",
                       font=('Helvetica', 12, 'bold'))
        style.map("Treeview.Heading",
                 background=[('active', self.colors['secondary'])])
        
        # Create main scrollable container
        self.main_scroll = ctk.CTkScrollableFrame(
            self.root,
            fg_color=self.colors['background'],
            corner_radius=0
        )
        self.main_scroll.pack(fill="both", expand=True)
        
        self.main_container = ctk.CTkFrame(self.main_scroll, fg_color=self.colors['background'])
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_header()
        
        # Add KPI Dashboard
        self.create_kpi_dashboard()
        
        # Upper section frame
        self.upper_section = ctk.CTkFrame(self.main_container, fg_color=self.colors['background'])
        self.upper_section.pack(fill="both", pady=(20, 10))
        
        # Lower section
        self.lower_section = ctk.CTkFrame(self.main_container, fg_color=self.colors['background'])
        self.lower_section.pack(fill="both", expand=True)
        
        # Define heights but allow them to be flexible
        self.upper_section.configure(height=350)
        self.lower_section.configure(height=350)
        
        self.content_frame = ctk.CTkFrame(self.upper_section, fg_color=self.colors['background'])
        self.content_frame.pack(fill="both", expand=True)
        
        # Frames and buttons
        self.create_frames()
        self.create_product_list()
        self.create_action_buttons()
        self.create_charts()
        
        self.load_products()
        
    def create_header(self):
        # Header frame
        header_frame = ctk.CTkFrame(
            self.main_container, 
            fg_color=self.colors['primary'], 
            height=100,
            corner_radius=10
        )
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Stock Manager Pro",
            font=self.fonts['heading'],
            text_color="white"
        )
        title_label.pack(side="left", padx=20, pady=20)
        
        # Summary statistics in card-like frames
        stats_frame = ctk.CTkFrame(header_frame, fg_color=self.colors['primary'])
        stats_frame.pack(side="right", padx=20, pady=20)
        
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM product")
        total_products = cursor.fetchone()[0]
        
        # Total stock value
        cursor.execute("SELECT SUM(price * quantity) FROM product")
        total_value = cursor.fetchone()[0] or 0
        
        # Stat cards
        self.create_stat_card(stats_frame, "Total Products", str(total_products), "📦")
        self.create_stat_card(stats_frame, "Total Stock Value", f"${total_value:,}", "💰")
        
    def create_stat_card(self, parent, title, value, icon):
        frame = ctk.CTkFrame(
            parent, 
            fg_color=self.colors['secondary'],
            corner_radius=8
        )
        frame.pack(side="left", padx=10)
        
        # Icon and title in one row
        title_frame = ctk.CTkFrame(frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=10, pady=(5, 0))
        
        icon_label = ctk.CTkLabel(
            title_frame,
            text=icon,
            font=("Segoe UI Emoji", 14),
            text_color="white"
        )
        icon_label.pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(
            title_frame,
            text=title,
            font=self.fonts['small'],
            text_color="white"
        ).pack(side="left")
        
        # Value
        ctk.CTkLabel(
            frame,
            text=value,
            font=self.fonts['subheading'],
            text_color="white"
        ).pack(padx=10, pady=(0, 5))
        
    def create_kpi_dashboard(self):
        # Create main frame for KPI dashboard
        kpi_frame = ctk.CTkFrame(self.main_container, fg_color=self.colors['background'])
        kpi_frame.pack(fill="x", pady=(0, 20))
        
        # Create grid for KPIs (2x2)
        for i in range(2):
            kpi_frame.grid_columnconfigure(i, weight=1)
        
        # Calculate KPI metrics
        cursor = self.conn.cursor()
        
        # Total Products
        cursor.execute("SELECT COUNT(*) FROM product")
        total_products = cursor.fetchone()[0]
        
        # Low Stock Items (items with quantity < 10)
        cursor.execute("SELECT COUNT(*) FROM product WHERE quantity < 10")
        low_stock = cursor.fetchone()[0]
        
        # Total Inventory Value
        cursor.execute("SELECT SUM(price * quantity) FROM product")
        total_value = cursor.fetchone()[0] or 0
        
        # Category Count
        cursor.execute("SELECT COUNT(*) FROM category")
        category_count = cursor.fetchone()[0]
        
        # Create KPI cards
        kpi_configs = [
            {
                'title': 'Total Products',
                'value': str(total_products),
                'icon': '📦',
                'color': self.colors['kpi_blue'],
                'position': (0, 0)
            },
            {
                'title': 'Low Stock Items',
                'value': str(low_stock),
                'icon': '⚠️',
                'color': self.colors['kpi_amber'],
                'position': (0, 1)
            },
            {
                'title': 'Total Inventory Value',
                'value': f'${total_value:,}',
                'icon': '💰',
                'color': self.colors['kpi_green'],
                'position': (1, 0)
            },
            {
                'title': 'Categories',
                'value': str(category_count),
                'icon': '🏷️',
                'color': self.colors['kpi_blue'],
                'position': (1, 1)
            }
        ]
        
        for kpi in kpi_configs:
            self.create_kpi_card(
                kpi_frame,
                title=kpi['title'],
                value=kpi['value'],
                icon=kpi['icon'],
                color=kpi['color'],
                row=kpi['position'][0],
                column=kpi['position'][1]
            )
    
    def create_kpi_card(self, parent, title, value, icon, color, row, column):
        # Create card frame
        card = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB"
        )
        card.grid(row=row, column=column, padx=10, pady=5, sticky="nsew")
        
        # Icon
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=("Segoe UI Emoji", 24),
            text_color=color
        )
        icon_label.pack(pady=(15, 5))
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=self.fonts['kpi_value'],
            text_color=color
        )
        value_label.pack(pady=(0, 5))
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=self.fonts['kpi_title'],
            text_color=self.colors['text']
        )
        title_label.pack(pady=(0, 15))
        
        # Make cards expand equally
        card.grid_propagate(False)
        card.configure(width=300, height=150)  # Fixed size for consistency
        
    def create_frames(self):
        # Frame for product lists
        self.left_frame = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=10)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.right_frame = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=10, width=320)
        self.right_frame.pack(side="right", fill="y", padx=(10, 0))
        self.right_frame.pack_propagate(False)
        
    def create_product_list(self):
        # Create a card for the product inventory
        product_card, product_content = self.create_card(
            self.left_frame, 
            title="Product Inventory",
            icon="📦"
        )
        product_card.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Search and pagination frame
        top_frame = ctk.CTkFrame(product_content, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 10))
        
        # Search frame
        search_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True)
        
        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search products...",
            width=300,
            textvariable=self.search_var,
            height=35,
            border_color=self.colors['primary']
        )
        search_entry.pack(side="left")
        
        # Pagination frame
        pagination_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        pagination_frame.pack(side="right")
        
        self.page_size_var = tk.StringVar(value="10")
        page_size_label = ctk.CTkLabel(
            pagination_frame,
            text="Items per page:",
            font=self.fonts['small']
        )
        page_size_label.pack(side="left", padx=(0, 5))
        
        page_size_combo = ctk.CTkComboBox(
            pagination_frame,
            values=["10", "25", "50", "100"],
            variable=self.page_size_var,
            width=70,
            height=35,
            command=self.load_products
        )
        page_size_combo.pack(side="left", padx=5)
        
        self.current_page = 1
        self.total_pages = 1
        
        self.page_label = ctk.CTkLabel(
            pagination_frame,
            text="Page 1 of 1",
            font=self.fonts['small']
        )
        self.page_label.pack(side="left", padx=10)
        
        prev_page_btn = ctk.CTkButton(
            pagination_frame,
            text="←",
            width=35,
            height=35,
            command=self.prev_page,
            fg_color=self.colors['primary']
        )
        prev_page_btn.pack(side="left", padx=2)
        
        next_page_btn = ctk.CTkButton(
            pagination_frame,
            text="→",
            width=35,
            height=35,
            command=self.next_page,
            fg_color=self.colors['primary']
        )
        next_page_btn.pack(side="left", padx=2)
        
        # Tree frame for product list
        self.tree_frame = ttk.Frame(product_content)
        self.tree_frame.pack(fill="both", expand=True, pady=(0, 5))
        
        # Configure Treeview style for alternating rows and hover effect
        style = ttk.Style()
        style.configure("Treeview",
                       background="#ffffff",
                       foreground=self.colors['text'],
                       rowheight=35,
                       fieldbackground="#ffffff",
                       bordercolor=self.colors['primary'],
                       borderwidth=0)
        
        # Configure alternating row colors
        style.map("Treeview",
                 background=[("selected", self.colors['primary'])],
                 foreground=[("selected", "white")])
        
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("ID", "Name", "Description", "Price", "Quantity", "Category"),
            show="headings",
            style="Treeview"
        )
        
        # Column headings with sorting
        columns = [
            ("ID", 80),
            ("Name", 200),
            ("Description", 300),
            ("Price", 100),
            ("Quantity", 100),
            ("Category", 150)
        ]
        
        self.sort_column = "ID"  # Default sort column
        self.sort_reverse = False  # Default sort direction
        
        for col, width in columns:
            self.tree.heading(col, text=col, anchor="w",
                            command=lambda c=col: self.sort_treeview(c))
            self.tree.column(col, width=width, anchor="w")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind events
        self.tree.bind("<Motion>", self.on_hover)  # Hover effect
        self.tree.bind("<Button-3>", self.show_context_menu)  # Right-click menu
        self.tree.bind("<Double-1>", self.on_double_click)  # Double-click to edit
        
        # Create context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self.edit_product_window)
        self.context_menu.add_command(label="Delete", command=self.delete_product)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="View Details", command=self.view_product_details)
        
        # Search functionality
        self.search_var.trace('w', self.filter_products)
        
        # Initial load with alternating colors
        self.load_products()

    def sort_treeview(self, col):
        """Sort tree contents when a column header is clicked"""
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False
        
        self.load_products()
    
    def on_hover(self, event):
        """Handle hover effect on tree items"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.set_tag_configure("hover", background="#f3f4f6")
            for prev_item in self.tree.tag_has("hover"):
                self.tree.item(prev_item, tags=[])
            self.tree.item(item, tags=["hover"])
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def on_double_click(self, event):
        """Handle double-click on tree item"""
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if item and column:
            self.start_inline_edit(item, column)
    
    def start_inline_edit(self, item, column):
        """Start inline editing for a cell"""
        if column in ("#1", "#6"):  # Don't allow editing ID or Category
            return
        
        # Get column name and current value
        col_name = self.tree.heading(column)["text"]
        current_value = self.tree.item(item)["values"][int(column[1]) - 1]
        
        # Create editing window
        edit_window = ctk.CTkToplevel(self.root)
        edit_window.geometry("300x150")
        edit_window.title(f"Edit {col_name}")
        
        value_var = tk.StringVar(value=str(current_value))
        
        ctk.CTkLabel(
            edit_window,
            text=f"Edit {col_name}:",
            font=self.fonts['body']
        ).pack(pady=(20, 5))
        
        entry = ctk.CTkEntry(
            edit_window,
            textvariable=value_var,
            width=200
        )
        entry.pack(pady=5)
        
        def save_changes():
            try:
                # Get all values
                values = list(self.tree.item(item)["values"])
                col_index = int(column[1]) - 1
                
                # Validate input based on column type
                if col_name in ("Price", "Quantity"):
                    new_value = int(value_var.get())
                else:
                    new_value = value_var.get()
                
                values[col_index] = new_value
                
                # Update database
                cursor = self.conn.cursor()
                if col_name == "Name":
                    cursor.execute("UPDATE product SET name = %s WHERE id = %s",
                                 (new_value, values[0]))
                elif col_name == "Description":
                    cursor.execute("UPDATE product SET description = %s WHERE id = %s",
                                 (new_value, values[0]))
                elif col_name == "Price":
                    cursor.execute("UPDATE product SET price = %s WHERE id = %s",
                                 (new_value, values[0]))
                elif col_name == "Quantity":
                    cursor.execute("UPDATE product SET quantity = %s WHERE id = %s",
                                 (new_value, values[0]))
                
                self.conn.commit()
                
                # Update tree
                self.tree.item(item, values=values)
                edit_window.destroy()
                self.update_charts()
                
            except ValueError:
                messagebox.showerror("Error", "Invalid value for numeric field")
            except Exception as e:
                messagebox.showerror("Error", f"Error updating value: {str(e)}")
        
        ctk.CTkButton(
            edit_window,
            text="Save",
            command=save_changes,
            fg_color=self.colors['success']
        ).pack(pady=20)
    
    def view_product_details(self):
        """Show detailed view of selected product"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to view")
            return
        
        values = self.tree.item(selected[0])["values"]
        
        details_window = ctk.CTkToplevel(self.root)
        details_window.geometry("500x400")
        details_window.title("Product Details")
        
        # Create a scrollable frame for details
        details_frame = ctk.CTkScrollableFrame(details_window)
        details_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Product details
        fields = [
            ("ID", values[0]),
            ("Name", values[1]),
            ("Description", values[2]),
            ("Price", f"${values[3]:,}"),
            ("Quantity", values[4]),
            ("Category", values[5])
        ]
        
        for label, value in fields:
            field_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
            field_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                field_frame,
                text=f"{label}:",
                font=("Helvetica", 12, "bold"),
                width=100,
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                field_frame,
                text=str(value),
                font=("Helvetica", 12),
                anchor="w"
            ).pack(side="left", padx=10)
    
    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_products()
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_products()
    
    def load_products(self, *args):
        """Load products with sorting and pagination"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        cursor = self.conn.cursor()
        
        # Get total count for pagination
        cursor.execute("SELECT COUNT(*) FROM product")
        total_items = cursor.fetchone()[0]
        
        # Calculate pagination
        page_size = int(self.page_size_var.get())
        self.total_pages = max(1, (total_items + page_size - 1) // page_size)
        self.current_page = min(self.current_page, self.total_pages)
        
        # Update page label
        self.page_label.configure(text=f"Page {self.current_page} of {self.total_pages}")
        
        # Map column names to their SQL counterparts
        column_map = {
            "ID": "p.id",
            "Name": "p.name",
            "Description": "p.description",
            "Price": "p.price",
            "Quantity": "p.quantity",
            "Category": "c.name"
        }
        
        # Prepare ORDER BY clause using the mapped column name
        order_by = f"ORDER BY {column_map[self.sort_column]}"
        if self.sort_reverse:
            order_by += " DESC"
        
        # Calculate offset
        offset = (self.current_page - 1) * page_size
        
        cursor.execute(f"""
            SELECT p.id, p.name, p.description, p.price, p.quantity, c.name 
            FROM product p 
            JOIN category c ON p.id_category = c.id
            {order_by}
            LIMIT %s OFFSET %s
        """, (page_size, offset))
        
        # Insert with alternating colors
        for i, product in enumerate(cursor.fetchall()):
            tags = ('evenrow',) if i % 2 == 0 else ('oddrow',)
            self.tree.insert("", "end", values=product, tags=tags)
        
        # Configure row colors
        self.tree.tag_configure('evenrow', background='#ffffff')
        self.tree.tag_configure('oddrow', background='#f3f4f6')
        self.tree.tag_configure('hover', background='#e5e7eb')

    def create_action_buttons(self):
        # Create a card for the actions section
        actions_card, actions_content = self.create_card(
            self.right_frame, 
            title="Actions",
            icon="⚙️"
        )
        actions_card.pack(fill="both", expand=True, padx=10, pady=10)
        
        filter_card, filter_content = self.create_card(
            actions_content,
            title="Filter by Category",
            icon="🏷️",
            height=90
        )
        filter_card.pack(fill="x", pady=(0, 10))  
        
        # Category dropdown with reduced height
        self.category_var = tk.StringVar()
        self.category_combobox = ctk.CTkComboBox(
            filter_content,
            variable=self.category_var,
            values=["All", "Electronics", "Clothing", "Food", "Books"],
            height=10,  
            width=200,
            fg_color="white",
            border_color=self.colors['primary'],
            button_color=self.colors['primary'],
            button_hover_color=self.colors['secondary'],
            dropdown_fg_color="white",
            dropdown_hover_color=self.colors['secondary'],
            dropdown_text_color=self.colors['text']
        )
        self.category_combobox.pack(fill="x", pady=(1, 7))  
        self.update_category_combobox()
        
        # Action buttons 
        button_frame = ctk.CTkFrame(actions_content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 5))
        
        
        button_height = 35
        button_corner_radius = 8
        button_padding = 3
        
        # Add Product button
        add_btn = ctk.CTkButton(
            button_frame,
            text="Add Product",
            command=self.add_product_window,
            fg_color=self.colors['success'],
            hover_color="#057857",  
            height=button_height, 
            corner_radius=button_corner_radius
        )
        add_btn.pack(fill="x", pady=button_padding) 
        
        # Edit Product button
        edit_btn = ctk.CTkButton(
            button_frame,
            text="Edit Product",
            command=self.edit_product_window,
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary'],
            height=button_height,  
            corner_radius=button_corner_radius
        )
        edit_btn.pack(fill="x", pady=button_padding)  
        
        # Delete Product button
        delete_btn = ctk.CTkButton(
            button_frame,
            text="Delete Product",
            command=self.delete_product,
            fg_color=self.colors['danger'],
            hover_color="#b91c1c",  
            height=button_height,  
            corner_radius=button_corner_radius
        )
        delete_btn.pack(fill="x", pady=button_padding) 

        # Add Category button
        add_category_btn = ctk.CTkButton(
            button_frame,
            text="Add Category",
            command=self.add_category_window,
            fg_color=self.colors['success'],
            hover_color="#057857",  
            height=button_height,
            corner_radius=button_corner_radius
        )
        add_category_btn.pack(fill="x", pady=button_padding)

        # Delete Category button
        delete_category_btn = ctk.CTkButton(
            button_frame,
            text="Delete Category",
            command=self.delete_category,
            fg_color=self.colors['danger'],
            hover_color="#b91c1c",  
            height=button_height,
            corner_radius=button_corner_radius
        )
        delete_category_btn.pack(fill="x", pady=button_padding)
        
        # Export Data button
        export_btn = ctk.CTkButton(
            button_frame,
            text="Export Data",
            command=self.export_data,
            fg_color=self.colors['warning'],
            hover_color="#b45309",  
            height=button_height, 
            corner_radius=button_corner_radius
        )
        export_btn.pack(fill="x", pady=button_padding)
        
    def create_charts(self):
        # Analytics dashboard section
        analytics_header = ctk.CTkFrame(self.lower_section, fg_color=self.colors['primary'], height=40)
        analytics_header.pack(fill="x", pady=(0, 10))
        analytics_header.pack_propagate(False)
        
        ctk.CTkLabel(
            analytics_header,
            text="Analytics Dashboard",
            font=self.fonts['heading'],
            text_color="white"
        ).pack(side="left", padx=20, pady=5)
        
        # Save tab selection when changed
        def save_tab_state(tab_name):
            try:
                with open('tab_state.txt', 'w') as f:
                    f.write(tab_name)
            except Exception as e:
                print(f"Error saving tab state: {e}")
        
        # Create tabview for analytics
        self.tab_view = ctk.CTkTabview(
            self.lower_section,
            fg_color="white",
            segmented_button_fg_color=self.colors['primary'],
            segmented_button_selected_color=self.colors['secondary'],
            segmented_button_selected_hover_color=self.colors['accent'],
            segmented_button_unselected_color=self.colors['primary'],
            segmented_button_unselected_hover_color=self.colors['secondary'],
            text_color="white",
            corner_radius=10,
            command=save_tab_state
        )
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create tabs
        overview_tab = self.tab_view.add("Overview")
        products_tab = self.tab_view.add("Products")
        categories_tab = self.tab_view.add("Categories")
        trends_tab = self.tab_view.add("Trends")
        
        # Configure grid layout for each tab
        for tab in [overview_tab, products_tab, categories_tab, trends_tab]:
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_columnconfigure(1, weight=1)
        
        # Store the charts frame for each tab
        self.charts_frames = {
            'overview': overview_tab,
            'products': products_tab,
            'categories': categories_tab,
            'trends': trends_tab
        }
        
        # Try to restore last selected tab
        try:
            with open('tab_state.txt', 'r') as f:
                last_tab = f.read().strip()
                if last_tab in ["Overview", "Products", "Categories", "Trends"]:
                    self.tab_view.set(last_tab)
        except:
            self.tab_view.set("Overview")
        
        self.update_charts()

    def update_charts(self):
        # Clear existing charts from all tabs
        for frame in self.charts_frames.values():
            for widget in frame.winfo_children():
                widget.destroy()
        
        # Set style for charts
        plt.style.use('ggplot')
        plt.rcParams.update({
            'font.size': 8,
            'axes.titlesize': 10,
            'axes.labelsize': 8,
            'xtick.labelsize': 7,
            'ytick.labelsize': 7,
            'legend.fontsize': 8,
            'figure.titlesize': 10,
            'figure.subplot.left': 0.15,
            'figure.subplot.right': 0.95,
            'figure.subplot.top': 0.9,
            'figure.subplot.bottom': 0.2,
            'figure.subplot.wspace': 0.3,
            'figure.subplot.hspace': 0.6
        })
        
        cursor = self.conn.cursor()
        
        # Define colors
        category_colors = ['#3b82f6', '#059669', '#d97706', '#dc2626', '#8b5cf6']
        bar_colors = ['#0891b2', '#0d9488', '#0284c7', '#4f46e5', '#7c3aed']
        hist_colors = ['#0ea5e9', '#06b6d4', '#0284c7', '#2563eb', '#4f46e5']
        top_products_colors = ['#f59e0b', '#d97706', '#b45309', '#92400e', '#78350f']
        
        # OVERVIEW TAB
        # Product Distribution
        overview_left_card, overview_left = self.create_card(
            self.charts_frames['overview'],
            title="Product Distribution",
            icon="📊"
        )
        overview_left_card.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        # Stock Value by Category
        overview_right_card, overview_right = self.create_card(
            self.charts_frames['overview'],
            title="Stock Value by Category",
            icon="💰"
        )
        overview_right_card.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        # PRODUCTS TAB
        # Price Distribution
        products_left_card, products_left = self.create_card(
            self.charts_frames['products'],
            title="Price Distribution",
            icon="📈"
        )
        products_left_card.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        # Top Products by Value
        products_right_card, products_right = self.create_card(
            self.charts_frames['products'],
            title="Top Products by Value",
            icon="🏆"
        )
        products_right_card.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        # Product Quantity Distribution
        products_bottom_card, products_bottom = self.create_card(
            self.charts_frames['products'],
            title="Quantity Distribution",
            icon="📦"
        )
        products_bottom_card.grid(row=1, column=0, columnspan=2, padx=15, pady=15, sticky="nsew")
        
        # CATEGORIES TAB
        # Category Distribution
        categories_left_card, categories_left = self.create_card(
            self.charts_frames['categories'],
            title="Products per Category",
            icon="🏷️"
        )
        categories_left_card.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        # Average Price by Category
        categories_right_card, categories_right = self.create_card(
            self.charts_frames['categories'],
            title="Average Price by Category",
            icon="💲"
        )
        categories_right_card.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        # TRENDS TAB
        # Low Stock Items
        trends_left_card, trends_left = self.create_card(
            self.charts_frames['trends'],
            title="Low Stock Items",
            icon="⚠️"
        )
        trends_left_card.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        # Value Distribution
        trends_right_card, trends_right = self.create_card(
            self.charts_frames['trends'],
            title="Value Distribution",
            icon="📊"
        )
        trends_right_card.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        # Create charts for Overview tab
        self.create_product_distribution_chart(overview_left, category_colors)
        self.create_stock_value_chart(overview_right, bar_colors)
        
        # Create charts for Products tab
        self.create_price_distribution_chart(products_left, hist_colors)
        self.create_top_products_chart(products_right, top_products_colors)
        self.create_quantity_distribution_chart(products_bottom, hist_colors)
        
        # Create charts for Categories tab
        self.create_category_distribution_chart(categories_left, category_colors)
        self.create_avg_price_chart(categories_right, bar_colors)
        
        # Create charts for Trends tab
        self.create_low_stock_chart(trends_left, bar_colors)
        self.create_value_distribution_chart(trends_right, hist_colors)

    def create_product_distribution_chart(self, parent, colors):
        fig, ax = plt.subplots(figsize=(7.5, 4), dpi=100)
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.name, COUNT(p.id) 
            FROM category c 
            LEFT JOIN product p ON c.id = p.id_category 
            GROUP BY c.name
        """)
        cat_data = cursor.fetchall()
        categories = [x[0] for x in cat_data]
        counts = [x[1] for x in cat_data]
        
        ax.set_position([0.36, 0.1, 0.5, 0.8])
        wedges, texts, autotexts = ax.pie(
            counts, 
            labels=categories, 
            autopct='%1.0f%%', 
            colors=colors[:len(categories)], 
            wedgeprops={'width': 0.6},
            textprops={'fontsize': 8},
            pctdistance=0.85,
            radius=0.8
        )
        
        plt.setp(autotexts, size=8, weight="bold", color="white")
        plt.setp(texts, size=8)
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def create_stock_value_chart(self, parent, colors):
        fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.name, SUM(p.price * p.quantity) 
            FROM category c 
            LEFT JOIN product p ON c.id = p.id_category 
            GROUP BY c.name
        """)
        value_data = cursor.fetchall()
        categories = [x[0] for x in value_data]
        values = [x[1] if x[1] is not None else 0 for x in value_data]
        
        bars = ax.bar(categories, values, color=colors[:len(categories)])
        ax.set_xlabel('Category', fontsize=10, labelpad=10)
        ax.set_ylabel('Value ($)', fontsize=10, labelpad=10)
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
        
        def format_value(x, p):
            if x >= 1e6:
                return f'${x/1e6:.1f}M'
            elif x >= 1e3:
                return f'${x/1e3:.1f}K'
            return f'${x:.0f}'
        
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_value))
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    format_value(height, None),
                    ha='center', va='bottom',
                    fontsize=8, fontweight='bold')
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def create_price_distribution_chart(self, parent, colors):
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        cursor = self.conn.cursor()
        cursor.execute("SELECT price FROM product")
        prices = [x[0] for x in cursor.fetchall()]
        
        n_bins = min(8, len(set(prices)))
        n, bins, patches = ax.hist(prices, bins=n_bins, edgecolor='white')
        
        for i, patch in enumerate(patches):
            patch.set_facecolor(colors[i % len(colors)])
        
        ax.set_xlabel('Price ($)', fontsize=10, labelpad=10)
        ax.set_ylabel('Count', fontsize=10, labelpad=10)
        
        if max(prices) > 1000:
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.1f}K' if x >= 1000 else f'${x:.0f}'))
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def create_top_products_chart(self, parent, colors):
        fig, ax = plt.subplots(figsize=(8.5, 5), dpi=100)
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name, price * quantity as total_value 
            FROM product 
            ORDER BY total_value DESC 
            LIMIT 5
        """)
        value_data = cursor.fetchall()
        
        products = [x[0] for x in value_data]
        values = [x[1] for x in value_data]
        
        bars = ax.barh(products, values, color=colors[:len(products)])
        
        ax.set_xlabel('Value ($)', fontsize=10, labelpad=10)
        
        def format_value(x, p):
            if x >= 1e6:
                return f'${x/1e6:.1f}M'
            elif x >= 1e3:
                return f'${x/1e3:.1f}K'
            return f'${x:.0f}'
        
        ax.xaxis.set_major_formatter(plt.FuncFormatter(format_value))
        
        plt.setp(ax.get_yticklabels(), fontsize=8)
        ax.set_ylim(-0.5, len(products) - 0.5)  # Add more space between bars
        
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, i, format_value(width, None),
                    ha='left', va='center',
                    fontsize=8, fontweight='bold')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def create_quantity_distribution_chart(self, parent, colors):
        fig, ax = plt.subplots(figsize=(12, 4), dpi=100)
        cursor = self.conn.cursor()
        cursor.execute("SELECT quantity FROM product")
        quantities = [x[0] for x in cursor.fetchall()]
        
        n_bins = min(10, len(set(quantities)))
        n, bins, patches = ax.hist(quantities, bins=n_bins, edgecolor='white')
        
        for i, patch in enumerate(patches):
            patch.set_facecolor(colors[i % len(colors)])
        
        ax.set_xlabel('Quantity', fontsize=10, labelpad=10)
        ax.set_ylabel('Number of Products', fontsize=10, labelpad=10)
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def create_category_distribution_chart(self, parent, colors):
        fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.name, COUNT(p.id) as product_count
            FROM category c
            LEFT JOIN product p ON c.id = p.id_category
            GROUP BY c.name
            ORDER BY product_count DESC
        """)
        data = cursor.fetchall()
        
        categories = [x[0] for x in data]
        counts = [x[1] for x in data]
        
        bars = ax.bar(categories, counts, color=colors[:len(categories)])
        ax.set_xlabel('Category', fontsize=10, labelpad=10)
        ax.set_ylabel('Number of Products', fontsize=10, labelpad=10)
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom',
                    fontsize=8, fontweight='bold')
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def create_avg_price_chart(self, parent, colors):
        fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.name, AVG(p.price) as avg_price
            FROM category c
            LEFT JOIN product p ON c.id = p.id_category
            GROUP BY c.name
            ORDER BY avg_price DESC
        """)
        data = cursor.fetchall()
        
        categories = [x[0] for x in data]
        avg_prices = [x[1] if x[1] is not None else 0 for x in data]
        
        bars = ax.bar(categories, avg_prices, color=colors[:len(categories)])
        ax.set_xlabel('Category', fontsize=10, labelpad=10)
        ax.set_ylabel('Average Price ($)', fontsize=10, labelpad=10)
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'${int(height)}',
                    ha='center', va='bottom',
                    fontsize=8, fontweight='bold')
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def create_low_stock_chart(self, parent, colors):
        fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name, quantity
            FROM product
            WHERE quantity < 10
            ORDER BY quantity
        """)
        data = cursor.fetchall()
        
        products = [x[0] for x in data]
        quantities = [x[1] for x in data]
        
        if not products:
            ax.text(0.5, 0.5, 'No products with low stock',
                    ha='center', va='center',
                    fontsize=12, color='gray')
        else:
            bars = ax.barh(products, quantities, color=colors[0])
            ax.set_xlabel('Quantity', fontsize=10, labelpad=10)
            plt.setp(ax.get_yticklabels(), fontsize=8)
            
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width, i, str(int(width)),
                        ha='left', va='center',
                        fontsize=8, fontweight='bold')
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def create_value_distribution_chart(self, parent, colors):
        fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
        cursor = self.conn.cursor()
        cursor.execute("SELECT price * quantity as value FROM product")
        values = [x[0] for x in cursor.fetchall()]
        
        n_bins = min(8, len(set(values)))
        n, bins, patches = ax.hist(values, bins=n_bins, edgecolor='white')
        
        for i, patch in enumerate(patches):
            patch.set_facecolor(colors[i % len(colors)])
        
        ax.set_xlabel('Total Value ($)', fontsize=10, labelpad=10)
        ax.set_ylabel('Number of Products', fontsize=10, labelpad=10)
        
        if max(values) > 1000:
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.1f}K' if x >= 1000 else f'${x:.0f}'))
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def filter_products(self, *args):
        search_term = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.id, p.name, p.description, p.price, p.quantity, c.name 
            FROM product p 
            JOIN category c ON p.id_category = c.id
        """)
        
        for product in cursor.fetchall():
            if (search_term in str(product[0]).lower() or  
                search_term in product[1].lower() or       
                search_term in product[2].lower() or      
                search_term in str(product[3]).lower() or  
                search_term in str(product[4]).lower() or  
                search_term in product[5].lower()):       
                self.tree.insert("", "end", values=product)

    def add_product_window(self):
        window = ctk.CTkToplevel(self.root)
        window.title("Add Product")
        window.geometry("500x700")
        window.configure(fg_color="white")
        

        ctk.CTkLabel(
            window,
            text="Add New Product",
            font=self.fonts['heading'],
            text_color=self.colors['text']
        ).pack(pady=(20, 30))
        
        name_var = tk.StringVar()
        desc_var = tk.StringVar()
        price_var = tk.StringVar()
        quantity_var = tk.StringVar()
        category_var = tk.StringVar()
        
    
        form_frame = ctk.CTkFrame(window, fg_color="white")
        form_frame.pack(fill="x", padx=40)
        
        self.create_form_field(form_frame, "Product Name:", name_var)
        self.create_form_field(form_frame, "Description:", desc_var)
        self.create_form_field(form_frame, "Price ($):", price_var)
        self.create_form_field(form_frame, "Quantity:", quantity_var)
        
        ctk.CTkLabel(
            form_frame,
            text="Category:",
            font=self.fonts['body']
        ).pack(fill="x", pady=(10, 0))
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM category")
        categories = [x[0] for x in cursor.fetchall()]
        
        category_combo = ctk.CTkComboBox(
            form_frame,
            variable=category_var,
            values=categories,
            height=35
        )
        category_combo.pack(fill="x", pady=(5, 15))
        
        def save_product():
            try:
                cursor = self.conn.cursor()
                # Get category id
                cursor.execute("SELECT id FROM category WHERE name = %s", (category_var.get(),))
                category_id = cursor.fetchone()[0]
                
                # Validate inputs
                if not all([name_var.get(), desc_var.get(), price_var.get(), quantity_var.get(), category_var.get()]):
                    messagebox.showwarning("Warning", "Please fill in all fields")
                    return
                
                cursor.execute("""
                    INSERT INTO product (name, description, price, quantity, id_category)
                    VALUES (%s, %s, %s, %s, %s)
                """, (name_var.get(), desc_var.get(), int(price_var.get()), 
                      int(quantity_var.get()), category_id))
                
                self.conn.commit()
                self.load_products()
                self.update_charts()
                window.destroy()
                messagebox.showinfo("Success", "Product added successfully!")
                
            except ValueError:
                messagebox.showerror("Error", "Price and Quantity must be numbers")
            except Exception as e:
                messagebox.showerror("Error", f"Error adding product: {str(e)}")
        
        ctk.CTkButton(
            window,
            text="Save Product",
            command=save_product,
            fg_color=self.colors['success'],
            hover_color=self.colors['success'],
            height=40
        ).pack(pady=30)
        
    def create_form_field(self, parent, label_text, variable):
        ctk.CTkLabel(
            parent,
            text=label_text,
            font=self.fonts['body']
        ).pack(fill="x", pady=(10, 0))
        
        ctk.CTkEntry(
            parent,
            textvariable=variable,
            height=35
        ).pack(fill="x", pady=(5, 15))

    def edit_product_window(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to edit")
            return
            
    
        values = self.tree.item(selected[0])['values']
        
        window = ctk.CTkToplevel(self.root)
        window.title("Edit Product")
        window.geometry("400x500")
        name_var = tk.StringVar(value=values[1])
        desc_var = tk.StringVar(value=values[2])
        price_var = tk.StringVar(value=values[3])
        quantity_var = tk.StringVar(value=values[4])
        category_var = tk.StringVar(value=values[5])
        
        ctk.CTkLabel(window, text="Name:").pack(pady=5)
        ctk.CTkEntry(window, textvariable=name_var).pack(pady=5)
        
        ctk.CTkLabel(window, text="Description:").pack(pady=5)
        ctk.CTkEntry(window, textvariable=desc_var).pack(pady=5)
        
        ctk.CTkLabel(window, text="Price:").pack(pady=5)
        ctk.CTkEntry(window, textvariable=price_var).pack(pady=5)
        
        ctk.CTkLabel(window, text="Quantity:").pack(pady=5)
        ctk.CTkEntry(window, textvariable=quantity_var).pack(pady=5)
        
        ctk.CTkLabel(window, text="Category:").pack(pady=5)
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM category")
        categories = [x[0] for x in cursor.fetchall()]
        category_combo = ctk.CTkComboBox(window, variable=category_var, values=categories)
        category_combo.pack(pady=5)
        
        def save_changes():
            try:
                cursor = self.conn.cursor()
                # Get category id
                cursor.execute("SELECT id FROM category WHERE name = %s", (category_var.get(),))
                category_id = cursor.fetchone()[0]
                
                # Update product
                cursor.execute("""
                    UPDATE product 
                    SET name = %s, description = %s, price = %s, quantity = %s, id_category = %s
                    WHERE id = %s
                """, (name_var.get(), desc_var.get(), int(price_var.get()), 
                      int(quantity_var.get()), category_id, values[0]))
                
                self.conn.commit()
                self.load_products()
                self.update_charts()
                window.destroy()
                messagebox.showinfo("Success", "Product updated successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error updating product: {str(e)}")
                
        ctk.CTkButton(window, text="Save Changes", command=save_changes).pack(pady=20)
        
    def delete_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to delete")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this product?"):
            try:
                cursor = self.conn.cursor()
                product_id = self.tree.item(selected[0])['values'][0]
                cursor.execute("DELETE FROM product WHERE id = %s", (product_id,))
                self.conn.commit()
                self.load_products()
                self.update_charts()
                messagebox.showinfo("Success", "Product deleted successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting product: {str(e)}")
                
    def add_category_window(self):
        window = ctk.CTkToplevel(self.root)
        window.title("Add Category")
        window.geometry("400x250")
        window.configure(fg_color="white")
        
        ctk.CTkLabel(
            window,
            text="Add New Category",
            font=self.fonts['heading'],
            text_color=self.colors['text']
        ).pack(pady=(20, 30))
        
        name_var = tk.StringVar()
        
        form_frame = ctk.CTkFrame(window, fg_color="white")
        form_frame.pack(fill="x", padx=40)
        
        ctk.CTkLabel(
            form_frame,
            text="Category Name:",
            font=self.fonts['body']
        ).pack(fill="x", pady=(10, 0))
        
        ctk.CTkEntry(
            form_frame,
            textvariable=name_var,
            height=35
        ).pack(fill="x", pady=(5, 15))
        
        def save_category():
            try:
                if not name_var.get().strip():
                    messagebox.showwarning("Warning", "Please enter a category name")
                    return
                
                cursor = self.conn.cursor()
                
                # Check if category already exists
                cursor.execute("SELECT COUNT(*) FROM category WHERE name = %s", (name_var.get(),))
                if cursor.fetchone()[0] > 0:
                    messagebox.showwarning("Warning", "Category already exists")
                    return
                
                cursor.execute("INSERT INTO category (name) VALUES (%s)", (name_var.get(),))
                self.conn.commit()
                
                self.update_category_combobox()
                self.update_charts()
                window.destroy()
                messagebox.showinfo("Success", "Category added successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error adding category: {str(e)}")
        
        ctk.CTkButton(
            window,
            text="Save Category",
            command=save_category,
            fg_color=self.colors['success'],
            hover_color=self.colors['success'],
            height=40
        ).pack(pady=30)

    def delete_category(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM category")
        categories = [x[0] for x in cursor.fetchall()]
        
        if not categories:
            messagebox.showwarning("Warning", "No categories available to delete")
            return
        
        window = ctk.CTkToplevel(self.root)
        window.title("Delete Category")
        window.geometry("400x300")
        window.configure(fg_color="white")
        
        ctk.CTkLabel(
            window,
            text="Delete Category",
            font=self.fonts['heading'],
            text_color=self.colors['text']
        ).pack(pady=(20, 30))
        
        category_var = tk.StringVar()
        
        form_frame = ctk.CTkFrame(window, fg_color="white")
        form_frame.pack(fill="x", padx=40)
        
        ctk.CTkLabel(
            form_frame,
            text="Select Category to Delete:",
            font=self.fonts['body']
        ).pack(fill="x", pady=(10, 0))
        
        category_combo = ctk.CTkComboBox(
            form_frame,
            variable=category_var,
            values=categories,
            height=35
        )
        category_combo.pack(fill="x", pady=(5, 15))
        
        def confirm_delete():
            if not category_var.get():
                messagebox.showwarning("Warning", "Please select a category")
                return
                
            if messagebox.askyesno("Confirm", f"Are you sure you want to delete the category '{category_var.get()}'?\n\nThis will also delete all products in this category!"):
                try:
                    cursor = self.conn.cursor()
                    
                    # Delete all products in the category first
                    cursor.execute("""
                        DELETE p FROM product p 
                        JOIN category c ON p.id_category = c.id 
                        WHERE c.name = %s
                    """, (category_var.get(),))
                    
                    # Then delete the category
                    cursor.execute("DELETE FROM category WHERE name = %s", (category_var.get(),))
                    self.conn.commit()
                    
                    self.update_category_combobox()
                    self.load_products()
                    self.update_charts()
                    window.destroy()
                    messagebox.showinfo("Success", "Category deleted successfully!")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Error deleting category: {str(e)}")
        
        ctk.CTkButton(
            window,
            text="Delete Category",
            command=confirm_delete,
            fg_color=self.colors['danger'],
            hover_color="#b91c1c",
            height=40
        ).pack(pady=30)

    def export_data(self):
        try:
            category = self.category_var.get()
            
            cursor = self.conn.cursor()
            if category and category != "All":
                cursor.execute("""
                    SELECT p.id, p.name, p.description, p.price, p.quantity, c.name as category
                    FROM product p 
                    JOIN category c ON p.id_category = c.id
                    WHERE c.name = %s
                """, (category,))
                filename = f"{category}_products.csv"
            else:
                cursor.execute("""
                    SELECT p.id, p.name, p.description, p.price, p.quantity, c.name as category
                    FROM product p 
                    JOIN category c ON p.id_category = c.id
                """)
                filename = "all_products.csv"
                
            columns = ['ID', 'Name', 'Description', 'Price', 'Quantity', 'Category']
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=columns)
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            export_dir = os.path.join(current_dir, "data-csv")
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            
            full_path = os.path.join(export_dir, filename)
            
            df.to_csv(full_path, index=False)
            messagebox.showinfo("Success", f"Data exported successfully to {full_path}")
            print(f"Data exported successfully to {full_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting data: {str(e)}")
            print(f"Export error details: {e}") 
            
    def update_category_combobox(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM category")
        categories = ["All"] + [x[0] for x in cursor.fetchall()]
        self.category_combobox.configure(values=categories)
        self.category_combobox.set("All")

    def create_card(self, parent, title=None, icon=None, width=None, height=None):
        """
        Creates a standardized card frame with optional title and icon.
        
        Args:
            parent: Parent widget
            title: Optional card title
            icon: Optional icon character (emoji)
            width: Optional fixed width
            height: Optional fixed height
            
        Returns:
            outer_frame: The card's outer frame
            content_frame: The inner content frame where widgets should be placed
        """
        # Create outer card frame with shadow effect
        outer_frame = ctk.CTkFrame(
            parent, 
            fg_color="white",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB"
        )
        
        if width:
            outer_frame.configure(width=width)
        if height:
            outer_frame.configure(height=height)
            outer_frame.pack_propagate(False)
        
        outer_frame.configure(border_width=1, border_color="#CCCCCC")
        
        if title:
            title_frame = ctk.CTkFrame(
                outer_frame,
                fg_color="#F9FAFB", 
                corner_radius=8,
                height=38  
            )
            title_frame.pack(fill="x", padx=10, pady=(10, 5)) 
            title_frame.pack_propagate(False)
            
            title_container = ctk.CTkFrame(title_frame, fg_color="transparent")
            title_container.pack(side="left", padx=10)
            
            if icon:
                icon_label = ctk.CTkLabel(
                    title_container,
                    text=icon,
                    font=("Segoe UI Emoji", 16), 
                    text_color=self.colors['primary']
                )
                icon_label.pack(side="left", padx=(0, 5))
            
            title_label = ctk.CTkLabel(
                title_container,
                text=title,
                font=('Helvetica', 15, 'bold'),  
                text_color=self.colors['text']
            )
            title_label.pack(side="left")
        
        
        content_frame = ctk.CTkFrame(outer_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=(0 if title else 15, 10))  
        
        return outer_frame, content_frame

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = StockManager()
    app.run() 