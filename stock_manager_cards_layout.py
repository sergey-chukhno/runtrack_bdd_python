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
            'text': '#1e293b' 
        }
    
        self.fonts = {
            'heading': ('Helvetica', 24, 'bold'),
            'subheading': ('Helvetica', 18, 'bold'),
            'body': ('Helvetica', 12),
            'small': ('Helvetica', 10)
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
        
        
        self.main_container = ctk.CTkFrame(self.root, fg_color=self.colors['background'])
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_header()
        
        # Upper section frame
        self.upper_section = ctk.CTkFrame(self.main_container, fg_color=self.colors['background'])
        self.upper_section.pack(fill="both", pady=(0, 10))
        
        # Lower section
        self.lower_section = ctk.CTkFrame(self.main_container, fg_color=self.colors['background'])
        self.lower_section.pack(fill="both", expand=True)
        
        # Define height of upper and lower sections (350 pixels for each)
        self.main_container.pack_propagate(False)
        self.upper_section.configure(height=350)  
        self.lower_section.configure(height=350)  
        self.upper_section.pack_propagate(False)
        self.lower_section.pack_propagate(False)
        
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
        
        # Search frame
        search_frame = ctk.CTkFrame(product_content, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 10))
        
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
        
        # Tree frame for product list
        self.tree_frame = ttk.Frame(product_content)
        self.tree_frame.pack(fill="both", expand=True, pady=(0, 5))
        
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("ID", "Name", "Description", "Price", "Quantity", "Category"),
            show="headings",
            style="Treeview"
        )
        
        # Column headings
        columns = [
            ("ID", 80),
            ("Name", 200),
            ("Description", 300),
            ("Price", 100),
            ("Quantity", 100),
            ("Category", 150)
        ]
        
        for col, width in columns:
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, width=width, anchor="w")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Search functionality
        self.search_var.trace('w', self.filter_products)
        
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
            font=self.fonts['subheading'],
            text_color="white"
        ).pack(side="left", padx=20, pady=5)
        
        # Canvas scrollbar
        canvas = tk.Canvas(self.lower_section, bg=self.colors['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.lower_section, orient="vertical", command=canvas.yview)
        
        self.charts_frame = ctk.CTkFrame(canvas, fg_color="white", corner_radius=10)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=(0, 10))
        
        canvas_frame = canvas.create_window((0, 0), window=self.charts_frame, anchor="nw")
        
        # Grid layout for charts
        self.charts_frame.grid_columnconfigure(0, weight=1)
        self.charts_frame.grid_columnconfigure(1, weight=1)
        self.charts_frame.grid_columnconfigure(2, weight=1)  
        
        # Bind the frame size to the canvas size
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_frame, width=canvas.winfo_width())
        
        def configure_canvas(event):
            # Update the window size when the canvas changes
            canvas.itemconfig(canvas_frame, width=canvas.winfo_width())
        
        # Bind events
        self.charts_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_canvas)
        
        # Enable scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        self.update_charts()
        
    def update_charts(self):
        for widget in self.charts_frame.winfo_children():
            widget.destroy()
        
        # Set style for charts
        plt.style.use('ggplot')
        
        # Charts styling
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
        
        # Create chart cards
        top_left_card, top_left = self.create_card(
            self.charts_frame, 
            title="Product Distribution",
            icon="📊"
        )
        top_left_card.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        top_right_card, top_right = self.create_card(
            self.charts_frame, 
            title="Stock Value by Category",
            icon="💰"
        )
        top_right_card.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        bottom_left_card, bottom_left = self.create_card(
            self.charts_frame, 
            title="Price Distribution",
            icon="📈"
        )
        bottom_left_card.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        
        bottom_right_card, bottom_right = self.create_card(
            self.charts_frame, 
            title="Top Products by Value",
            icon="🏆"
        )
        bottom_right_card.grid(row=1, column=1, padx=15, pady=15, sticky="nsew")
        
        # Define colors for charts
        category_colors = ['#3b82f6', '#059669', '#d97706', '#dc2626', '#8b5cf6']
        bar_colors = ['#0891b2', '#0d9488', '#0284c7', '#4f46e5', '#7c3aed']
        hist_colors = ['#0ea5e9', '#06b6d4', '#0284c7', '#2563eb', '#4f46e5']
        top_products_colors = ['#f59e0b', '#d97706', '#b45309', '#92400e', '#78350f']
        
        # Product Distribution by Category (Pie Chart)
        fig1, ax1 = plt.subplots(figsize=(7.5, 4), dpi=100)
        cursor.execute("""
            SELECT c.name, COUNT(p.id) 
            FROM category c 
            LEFT JOIN product p ON c.id = p.id_category 
            GROUP BY c.name
        """)
        cat_data = cursor.fetchall()
        categories = [x[0] for x in cat_data]
        counts = [x[1] for x in cat_data]
        
        ax1.set_position([0.36, 0.1, 0.5, 0.8])
        
        wedges, texts, autotexts = ax1.pie(counts, 
                                          labels=categories, 
                                          autopct='%1.0f%%', 
                                          colors=category_colors, 
                                          wedgeprops={'width': 0.6},
                                          textprops={'fontsize': 8},
                                          pctdistance=0.85,
                                          radius=0.8,  
                                          labeldistance=1.1)
        
        plt.setp(autotexts, size=8, weight="bold", color="white")
        plt.setp(texts, size=8)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        
        canvas1 = FigureCanvasTkAgg(fig1, master=top_left)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        # Stock Value by Category (Bar Chart)
        fig2, ax2 = plt.subplots(figsize=(7, 4), dpi=100)
        cursor.execute("""
            SELECT c.name, SUM(p.price * p.quantity) 
            FROM category c 
            LEFT JOIN product p ON c.id = p.id_category 
            GROUP BY c.name
        """)
        value_data = cursor.fetchall()
        categories = [x[0] for x in value_data]
        values = [x[1] if x[1] is not None else 0 for x in value_data]
        
        bars = ax2.bar(categories, values, color=bar_colors[:len(categories)])
        ax2.set_xlabel('Category', fontsize=10, labelpad=10)
        ax2.set_ylabel('Value ($)', fontsize=10, labelpad=10)
        plt.setp(ax2.get_xticklabels(), rotation=30, ha='right')
        
        def format_value(x, p):
            if x >= 1e6:
                return f'${x/1e6:.1f}M'
            elif x >= 1e3:
                return f'${x/1e3:.1f}K'
            return f'${x:.0f}'
        
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(format_value))
        
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    format_value(height, None),
                    ha='center', va='bottom',
                    fontsize=8, fontweight='bold')
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        canvas2 = FigureCanvasTkAgg(fig2, master=top_right)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        # Price Distribution (Histogram)
        fig3, ax3 = plt.subplots(figsize=(6, 4), dpi=100)
        cursor.execute("SELECT price FROM product")
        prices = [x[0] for x in cursor.fetchall()]
        
        n_bins = min(8, len(set(prices)))
        n, bins, patches = ax3.hist(prices, bins=n_bins, edgecolor='white')
        
        for i, patch in enumerate(patches):
            patch.set_facecolor(hist_colors[i % len(hist_colors)])
        
        ax3.set_xlabel('Price ($)', fontsize=10, labelpad=10)
        ax3.set_ylabel('Count', fontsize=10, labelpad=10)
        
        if max(prices) > 1000:
            ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.1f}K' if x >= 1000 else f'${x:.0f}'))
        
        plt.tight_layout()
        canvas3 = FigureCanvasTkAgg(fig3, master=bottom_left)
        canvas3.draw()
        canvas3.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        # Top Products by Value (Horizontal Bar Chart)
        fig4, ax4 = plt.subplots(figsize=(8.5, 5), dpi=100)
        cursor.execute("""
            SELECT name, price * quantity as total_value 
            FROM product 
            ORDER BY total_value DESC 
            LIMIT 5
        """)
        value_data = cursor.fetchall()
        
        products = [x[0] for x in value_data]
        values = [x[1] for x in value_data]
        
        bars = ax4.barh(products, values, color=top_products_colors[:len(products)])
        
        ax4.set_xlabel('Value ($)', fontsize=10, labelpad=10)
        
        ax4.xaxis.set_major_formatter(plt.FuncFormatter(format_value))
        
        plt.setp(ax4.get_yticklabels(), fontsize=8)
        ax4.set_ylim(-0.5, len(products) - 0.5)  # Add more space between bars
        
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax4.text(width, i, format_value(width, None),
                    ha='left', va='center',
                    fontsize=8, fontweight='bold')
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        
        canvas4 = FigureCanvasTkAgg(fig4, master=bottom_right)
        canvas4.draw()
        canvas4.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

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

    def load_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.id, p.name, p.description, p.price, p.quantity, c.name 
            FROM product p 
            JOIN category c ON p.id_category = c.id
        """)
        
        for product in cursor.fetchall():
            self.tree.insert("", "end", values=product)

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