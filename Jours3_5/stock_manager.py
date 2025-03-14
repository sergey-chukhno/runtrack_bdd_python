import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import mysql.connector
import pandas as pd
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from datetime import datetime
from PIL import Image , ImageTk
import os
from dotenv import load_dotenv
import json
from textwrap import wrap
import gc  # Import garbage collector for memory management

load_dotenv()

class StockManager:
    def __init__(self):
        # Initialize themed widgets registry
        self._themed_widgets = []
        self.load_theme_preference()
        self.setup_color_schemes()
        self.setup_database()
        self.setup_gui()
        
    def register_themed_widget(self, widget, widget_type):
        self._themed_widgets.append((widget, widget_type))
        return widget
    
    def create_themed_entry(self, parent, **kwargs):
        theme_props = {
            "fg_color": "white" if self.current_theme == "light" else self.colors['card_bg'],
            "text_color": self.colors['text'],
            "border_color": self.colors['primary'],
            "placeholder_text_color": self.colors['text']
        }
        
        
        for prop, value in theme_props.items():
            if prop not in kwargs:
                kwargs[prop] = value
        
        # Create the widget
        widget = ctk.CTkEntry(parent, **kwargs)
        
        # Register for theme updates
        self.register_themed_widget(widget, "CTkEntry")
        return widget
    
    def create_themed_combobox(self, parent, **kwargs):
        # Ensure the theme colors (dark mode/light mode) are explicitly set
        bg_color = "white" if self.current_theme == "light" else self.colors['card_bg']
        
        theme_props = {
            "fg_color": bg_color,
            "text_color": self.colors['text'],
            "button_color": self.colors['primary'],
            "button_hover_color": self.colors['secondary'],
            "border_color": self.colors['primary'],
            "dropdown_fg_color": bg_color,
            "dropdown_hover_color": self.colors['hover'],
            "dropdown_text_color": self.colors['text']
        }
        
        for prop, value in theme_props.items():
            if prop not in kwargs:
                kwargs[prop] = value
        
        widget = ctk.CTkComboBox(parent, **kwargs)
        
        widget.configure(
            fg_color=bg_color,
            dropdown_fg_color=bg_color
        )
        
        self.register_themed_widget(widget, "CTkComboBox")
        return widget
        
    def update_themed_widgets(self):
        """Update all registered themed widgets"""
        for widget, widget_type in self._themed_widgets[:]:
            try:
                if widget.winfo_exists():
                    if widget_type == "CTkEntry":
                        widget.configure(
                            fg_color="white" if self.current_theme == "light" else self.colors['card_bg'],
                            text_color=self.colors['text'],
                            border_color=self.colors['primary']
                        )
                    elif widget_type == "CTkComboBox":
                        widget.configure(
                            fg_color="white" if self.current_theme == "light" else self.colors['card_bg'],
                            text_color=self.colors['text'],
                            button_color=self.colors['primary'],
                            button_hover_color=self.colors['secondary'],
                            border_color=self.colors['primary'],
                            dropdown_fg_color="white" if self.current_theme == "light" else self.colors['card_bg'],
                            dropdown_hover_color=self.colors['hover'],
                            dropdown_text_color=self.colors['text']
                        )
                else:
                    # Remove widget if it no longer exists
                    self._themed_widgets.remove((widget, widget_type))
            except Exception as e:
                print(f"Error updating themed widget: {e}")
                # Remove problematic widget from registry
                self._themed_widgets.remove((widget, widget_type))
    
    def load_theme_preference(self):
        try:
            with open('theme_preference.json', 'r') as f:
                preference = json.load(f)
                self.current_theme = preference.get('theme', 'light')
                ctk.set_appearance_mode(self.current_theme)
        except:
            self.current_theme = 'light'
            ctk.set_appearance_mode('light')
            
    def save_theme_preference(self):
        try:
            with open('theme_preference.json', 'w') as f:
                json.dump({'theme': self.current_theme}, f)
        except Exception as e:
            print(f"Error saving theme preference: {e}")
            
    def setup_color_schemes(self):
        self.color_schemes = {
            'light': {
                'primary': '#2563eb',
                'secondary': '#3b82f6',
                'accent': '#1d4ed8',
                'success': '#059669',
                'warning': '#d97706',
                'danger': '#dc2626',
                'background': '#ffffff',  
                'text': '#1e293b',
                'card_bg': '#ffffff',
                'card_border': '#e2e8f0',
                'hover': '#f8fafc',
                'kpi_blue': '#3b82f6',
                'kpi_amber': '#f59e0b',
                'kpi_green': '#10b981',
                'kpi_red': '#ef4444'
            },
            'dark': {
                'primary': '#3b82f6',
                'secondary': '#60a5fa',
                'accent': '#2563eb',
                'success': '#10b981',
                'warning': '#f59e0b',
                'danger': '#ef4444',
                'background': '#0f172a',
                'text': '#f8fafc',
                'card_bg': '#1e293b',
                'card_border': '#374151',
                'hover': '#2d3748',
                'kpi_blue': '#60a5fa',
                'kpi_amber': '#fbbf24',
                'kpi_green': '#34d399',
                'kpi_red': '#f87171'
            }
        }
        
        self.chart_color_schemes = {
            'light': {
                'category_colors': ['#3b82f6', '#059669', '#d97706', '#dc2626', '#8b5cf6'],
                'bar_colors': ['#0891b2', '#0d9488', '#0284c7', '#4f46e5', '#7c3aed'],
                'hist_colors': ['#0ea5e9', '#06b6d4', '#0284c7', '#2563eb', '#4f46e5'],
                'top_products_colors': ['#f59e0b', '#d97706', '#b45309', '#92400e', '#78350f']
            },
            'dark': {
                'category_colors': ['#60a5fa', '#34d399', '#fbbf24', '#f87171', '#c084fc'],
                'bar_colors': ['#22d3ee', '#2dd4bf', '#38bdf8', '#818cf8', '#a78bfa'],
                'hist_colors': ['#38bdf8', '#22d3ee', '#60a5fa', '#6366f1', '#818cf8'],
                'top_products_colors': ['#fbbf24', '#f59e0b', '#fb923c', '#fdba74', '#fed7aa']
            }
        }
        
        self.colors = self.color_schemes[self.current_theme]
        self.chart_colors = self.chart_color_schemes[self.current_theme]
        
    def toggle_theme(self):
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        ctk.set_appearance_mode(self.current_theme)
        self.colors = self.color_schemes[self.current_theme]
        self.chart_colors = self.chart_color_schemes[self.current_theme]
        self.save_theme_preference()
        
    
        self.update_theme()
        
    def update_theme(self):
        # First update all registered themed widgets
        self.update_themed_widgets()
        
        self.main_container.configure(fg_color=self.colors['background'])
        self.main_scroll.configure(fg_color=self.colors['background'])
        
        self.header_frame.configure(fg_color=self.colors['primary'])
        
        if hasattr(self, 'kpi_frame'):
            self.kpi_frame.configure(fg_color=self.colors['background'])
        
        for widget in self.root.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                self.update_widget_theme(widget)
        
        style = ttk.Style()
        
        style.configure("Treeview",
                       background=self.colors['card_bg'],
                       foreground=self.colors['text'],
                       fieldbackground=self.colors['card_bg'])
        
        style.configure("Treeview.Heading",
                       background=self.colors['primary'],
                       foreground="white")
        
        # Configure selection colors
        style.map("Treeview",
                 background=[("selected", self.colors['primary']),
                           ("!selected", self.colors['card_bg'])],
                 foreground=[("selected", "white"),
                           ("!selected", self.colors['text'])])
        self.tree.tag_configure('evenrow', 
                              background=self.colors['card_bg'],
                              foreground=self.colors['text'])
        self.tree.tag_configure('oddrow', 
                              background=self.colors['hover'],
                              foreground=self.colors['text'])
        
        # Update hover effect
        self.tree.tag_configure('hover',
                              background=self.colors['primary'],
                              foreground='white')
        
        # Update frames
        self.left_frame.configure(fg_color=self.colors['card_bg'])
        self.right_frame.configure(fg_color=self.colors['card_bg'])
        
        self.upper_section.configure(fg_color=self.colors['background'])
        self.lower_section.configure(fg_color=self.colors['background'])
        self.content_frame.configure(fg_color=self.colors['background'])
        
        for widget in self.main_container.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget != self.header_frame:
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkFrame):
                        child.configure(fg_color=self.colors['card_bg'])
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, ctk.CTkLabel):
                                grandchild.configure(text_color=self.colors['text'])
        for card in self.left_frame.winfo_children() + self.right_frame.winfo_children():
            if isinstance(card, ctk.CTkFrame):
                card.configure(fg_color=self.colors['card_bg'])
                for child in card.winfo_children():
                    if isinstance(child, ctk.CTkFrame) and 'transparent' not in str(child.cget('fg_color')):
                        if 'hover' in str(child.cget('fg_color')):
                            child.configure(fg_color=self.colors['hover'])
                        else:
                            child.configure(fg_color=self.colors['card_bg'])
        
        if hasattr(self, 'tab_view'):
            self.tab_view.configure(
                fg_color=self.colors['card_bg'],
                segmented_button_fg_color=self.colors['primary'],
                segmented_button_selected_color=self.colors['secondary'],
                segmented_button_selected_hover_color=self.colors['accent'],
                segmented_button_unselected_color=self.colors['primary'],
                segmented_button_unselected_hover_color=self.colors['secondary'],
                text_color=self.colors['text']
            )
            
            for tab_name in self.tab_view._tab_dict:
                tab = self.tab_view._tab_dict[tab_name]
                tab.configure(fg_color=self.colors['card_bg'])
        
        # Update charts with new color scheme
        self.update_charts()
        
        self.load_products()
        
    def update_widget_theme(self, widget):
        if isinstance(widget, ctk.CTkFrame):
            if 'transparent' not in str(widget.cget('fg_color')):
                widget.configure(fg_color=self.colors['card_bg'])
            for child in widget.winfo_children():
                self.update_widget_theme(child)
        elif isinstance(widget, ctk.CTkLabel):
            widget.configure(text_color=self.colors['text'])
        elif isinstance(widget, ctk.CTkButton):
            if 'success' in str(widget.cget('fg_color')):
                widget.configure(fg_color=self.colors['success'])
            elif 'danger' in str(widget.cget('fg_color')):
                widget.configure(fg_color=self.colors['danger'])
            elif 'warning' in str(widget.cget('fg_color')):
                widget.configure(fg_color=self.colors['warning'])
            else:
                widget.configure(fg_color=self.colors['primary'])
        elif isinstance(widget, ctk.CTkTabview):
            widget.configure(
                fg_color=self.colors['card_bg'],
                segmented_button_fg_color=self.colors['primary'],
                segmented_button_selected_color=self.colors['secondary'],
                segmented_button_selected_hover_color=self.colors['accent'],
                segmented_button_unselected_color=self.colors['primary'],
                segmented_button_unselected_hover_color=self.colors['secondary']
            )
            for tab_name in widget._tab_dict:
                tab = widget._tab_dict[tab_name]
                tab.configure(fg_color=self.colors['card_bg'])
                for child in tab.winfo_children():
                    self.update_widget_theme(child)
        
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
        ctk.set_appearance_mode(self.current_theme)
        
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
                       background=self.colors['card_bg'],
                       foreground=self.colors['text'],
                       rowheight=30,
                       fieldbackground=self.colors['card_bg'],
                       bordercolor=self.colors['primary'],
                       borderwidth=0)
        style.configure("Treeview.Heading",
                       background=self.colors['primary'],
                       foreground="white",
                       relief="flat",
                       font=('Helvetica', 12, 'bold'))
        style.map("Treeview.Heading",
                 background=[('active', self.colors['secondary'])])
        style.map("Treeview",
                 background=[("selected", self.colors['primary']),
                           ("!selected", self.colors['card_bg'])],
                 foreground=[("selected", "white"),
                           ("!selected", self.colors['text'])])
        
        # Main scrollable container
        self.main_scroll = ctk.CTkScrollableFrame(
            self.root,
            fg_color=self.colors['background'],
            corner_radius=0
        )
        self.main_scroll.pack(fill="both", expand=True)
        
        self.main_container = ctk.CTkFrame(self.main_scroll, fg_color=self.colors['background'])
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_header()
        
        # KPI Dashboard
        self.create_kpi_dashboard()
        
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
        self.header_frame = ctk.CTkFrame(
            self.main_container, 
            fg_color=self.colors['primary'], 
            height=100,
            corner_radius=10
        )
        self.header_frame.pack(fill="x", pady=(0, 20))
        self.header_frame.pack_propagate(False)
        
        # Left side with title
        title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Stock Manager Pro",
            font=self.fonts['heading'],
            text_color="white"
        )
        title_label.pack(side="left", padx=(0, 20))
        
        # Theme toggle switch
        switch_var = ctk.StringVar(value="on" if self.current_theme == "dark" else "off")
        theme_switch = ctk.CTkSwitch(
            title_frame,
            text="Dark Mode",
            command=self.toggle_theme,
            variable=switch_var,
            onvalue="on",
            offvalue="off",
            button_color=self.colors['accent'],
            button_hover_color=self.colors['secondary'],
            progress_color=self.colors['secondary'],
            text_color="white"
        )
        theme_switch.pack(side="left", padx=20)
        
        # Stats frames
        stats_frame = ctk.CTkFrame(self.header_frame, fg_color=self.colors['primary'])
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
        
        
        ctk.CTkLabel(
            frame,
            text=value,
            font=self.fonts['subheading'],
            text_color="white"
        ).pack(padx=10, pady=(0, 5))
        
    def create_kpi_dashboard(self):
        self.kpi_frame = ctk.CTkFrame(self.main_container, fg_color=self.colors['background'])
        self.kpi_frame.pack(fill="x", pady=(0, 20))
        
        # KPI grid
        for i in range(2):
            self.kpi_frame.grid_columnconfigure(i, weight=1)
        
        # KPI Metrics
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
        
        # KPI cards
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
                self.kpi_frame,
                title=kpi['title'],
                value=kpi['value'],
                icon=kpi['icon'],
                color=kpi['color'],
                row=kpi['position'][0],
                column=kpi['position'][1]
            )
    
    def create_kpi_card(self, parent, title, value, icon, color, row, column):
        # Card frame
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors['card_bg'],
            corner_radius=10,
            border_width=1,
            border_color=self.colors['card_border']
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
        
        # Equal size for cards
        card.grid_propagate(False)
        card.configure(width=300, height=150) 
        
    def create_frames(self):
        # Frame for product list and filters
        self.left_frame = ctk.CTkFrame(self.content_frame, fg_color=self.colors['card_bg'], corner_radius=10)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.right_frame = ctk.CTkFrame(self.content_frame, fg_color=self.colors['card_bg'], corner_radius=10, width=320)
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
        
        # Search container with rounded corners and background
        search_container = ctk.CTkFrame(
            top_frame,
            fg_color=self.colors['hover'],
            corner_radius=15,
            height=40
        )
        search_container.pack(side="left", fill="x", expand=True)
        
        inner_container = ctk.CTkFrame(search_container, fg_color="transparent")
        inner_container.pack(fill="x", padx=5, pady=5)
        
        search_icon = ctk.CTkLabel(
            inner_container,
            text="🔍",
            font=("Segoe UI Emoji", 14),
            text_color=self.colors['text']
        )
        search_icon.pack(side="left", padx=(5, 0))
        
        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(
            inner_container,
            placeholder_text="Search by name, description, price, etc...",
            textvariable=self.search_var,
            border_width=0,  
            fg_color="transparent", 
            placeholder_text_color=self.colors['text'] if self.current_theme == 'dark' else '#A0A0A0',
            text_color=self.colors['text'],
            corner_radius=0, 
            height=30  
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(5, 10), pady=0)
        
        # Add search trace to filter products as typing
        self.search_var.trace('w', self.filter_products)
        
        # Advanced filters button intgrated with search container
        self.filters_active = False  # Track if filters are active
        self.advanced_filters_btn = ctk.CTkButton(
            inner_container,
            text="Filters",
            command=self.show_advanced_filters,
            width=80,
            height=30,  
            corner_radius=15,
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary'],
            text_color="white"
        )
        self.advanced_filters_btn.pack(side="right", padx=(3, 5))
        
        self.init_filter_state()
        
        # Pagination 
        pagination_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        pagination_frame.pack(side="right")
        
        self.page_size_var = tk.StringVar(value="10")
        page_size_label = ctk.CTkLabel(
            pagination_frame,
            text="Items per page:",
            font=self.fonts['small'],
            text_color=self.colors['text']
        )
        page_size_label.pack(side="left", padx=(0, 5))
        
        page_size_combo = self.create_themed_combobox(
            pagination_frame,
            values=["10", "25", "50", "100"],
            variable=self.page_size_var,
            width=70,
            height=35,
            command=self.load_products,
            text_color=self.colors['text'],
            button_color=self.colors['primary'],
            button_hover_color=self.colors['secondary'],
            border_color=self.colors['primary'],
            dropdown_fg_color="white" if self.current_theme == "light" else self.colors['card_bg'],
            dropdown_text_color=self.colors['text'],
            dropdown_hover_color=self.colors['hover']
        )
        page_size_combo.pack(side="left", padx=5)
        
        self.current_page = 1
        self.total_pages = 1
        
        self.page_label = ctk.CTkLabel(
            pagination_frame,
            text="Page 1 of 1",
            font=self.fonts['small'],
            text_color=self.colors['text']
        )
        self.page_label.pack(side="left", padx=10)
        
        prev_page_btn = ctk.CTkButton(
            pagination_frame,
            text="←",
            width=35,
            height=35,
            command=self.prev_page,
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary']
        )
        prev_page_btn.pack(side="left", padx=2)
        
        next_page_btn = ctk.CTkButton(
            pagination_frame,
            text="→",
            width=35,
            height=35,
            command=self.next_page,
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary']
        )
        next_page_btn.pack(side="left", padx=2)
        
        # Tree frame for product list
        self.tree_frame = ttk.Frame(product_content)
        self.tree_frame.pack(fill="both", expand=True, pady=(0, 5))
        
        style = ttk.Style()
        style.configure("Treeview",
                       background=self.colors['card_bg'],
                       foreground=self.colors['text'],
                       rowheight=35,
                       fieldbackground=self.colors['card_bg'])
        
        style.configure("Treeview.Heading",
                       background=self.colors['primary'],
                       foreground="white")
        
        style.map("Treeview",
                 background=[("selected", self.colors['primary']),
                           ("!selected", self.colors['card_bg'])],
                 foreground=[("selected", "white"),
                           ("!selected", self.colors['text'])])
        
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
        
        self.tree.tag_configure('evenrow', background=self.colors['card_bg'])
        self.tree.tag_configure('oddrow', background=self.colors['hover'])
        self.tree.tag_configure('hover', background=self.colors['primary'], foreground='white')
        
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
        
        self.load_products()

    def sort_treeview(self, col):
        # Sorting Product Table by clicking on column name
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False
        
        self.load_products()
    
    def on_hover(self, event):
        # Handle hover effect on Product Table rows
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.tag_configure("hover", 
                                  background=self.colors['primary'],
                                  foreground="white")
            for prev_item in self.tree.tag_has("hover"):
                self.tree.item(prev_item, tags=[])
            self.tree.item(item, tags=["hover"])
    
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def on_double_click(self, event):
        # Handle double click to edit product 
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if item and column:
            self.start_inline_edit(item, column)
    
    def start_inline_edit(self, item, column):
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
                values = list(self.tree.item(item)["values"])
                col_index = int(column[1]) - 1
                
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
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to view")
            return
        
        values = self.tree.item(selected[0])["values"]

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_products()
    
    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_products()
    
    def load_products(self, *args):
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
        
        # Map column names to SQL column names
        column_map = {
            "ID": "p.id",
            "Name": "p.name",
            "Description": "p.description",
            "Price": "p.price",
            "Quantity": "p.quantity",
            "Category": "c.name"
        }
        
        order_by = f"ORDER BY {column_map[self.sort_column]}"
        if self.sort_reverse:
            order_by += " DESC"
        
        # Calculate offset (based on current page)
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
        
        # Configure row colors based on current theme
        self.tree.tag_configure('evenrow', 
                              background=self.colors['card_bg'],
                              foreground=self.colors['text'])
        self.tree.tag_configure('oddrow', 
                              background=self.colors['hover'],
                              foreground=self.colors['text'])
        self.tree.tag_configure('hover', 
                              background=self.colors['primary'],
                              foreground='white')

    def create_action_buttons(self):
        # Create a card for the actions section
        actions_card, actions_content = self.create_card(
            self.right_frame,
            title="Actions",
            icon="⚙️"
        )
        actions_card.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Action buttons 
        button_frame = ctk.CTkFrame(actions_content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 5))
        
        button_height = 35
        button_corner_radius = 8
        button_padding = 3
        
        # Add Product
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
        
        
        # Export Data button in its own frame at the bottom
        export_frame = ctk.CTkFrame(actions_content, fg_color="transparent")
        export_frame.pack(fill="x", side="bottom")
        
        export_btn = ctk.CTkButton(
            export_frame,
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
        
        try:
            with open('tab_state.txt', 'r') as f:
                self.last_tab = f.read().strip()
        except:
            self.last_tab = "Overview"
        
        # Analytics tabview
        self.tab_view = ctk.CTkTabview(
            self.lower_section,
            fg_color=self.colors['card_bg'],
            segmented_button_fg_color=self.colors['primary'],
            segmented_button_selected_color=self.colors['secondary'],
            segmented_button_selected_hover_color=self.colors['accent'],
            segmented_button_unselected_color=self.colors['primary'],
            segmented_button_unselected_hover_color=self.colors['secondary'],
            text_color=self.colors['text'],
            corner_radius=10,
            command=lambda tab_name: self.save_tab_state(tab_name)  
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
            tab.configure(fg_color=self.colors['card_bg'])
        
        self.charts_frames = {
            'overview': overview_tab,
            'products': products_tab,
            'categories': categories_tab,
            'trends': trends_tab
        }
        
        # Initial tab (Overview)
        if self.last_tab in ["Overview", "Products", "Categories", "Trends"]:
            self.tab_view.set(self.last_tab)
        else:
            self.tab_view.set("Overview")
        
        self.update_charts()
        
    def save_tab_state(self, tab_name):
        try:
            with open('tab_state.txt', 'w') as f:
                f.write(tab_name)
            self.last_tab = tab_name
        except Exception as e:
            print(f"Error saving tab state: {e}")
        
    def update_charts(self):
        try:
            for frame in self.charts_frames.values():
                for widget in frame.winfo_children():
                    widget.destroy()

            # Close all existing figures and collect garbage
            plt.close('all')
            gc.collect()

            plt.style.use('seaborn-v0_8-darkgrid' if self.current_theme == 'dark' else 'seaborn-v0_8')

            bg_color = self.colors['card_bg']
            text_color = self.colors['text']

            plt.rcParams.update({
                'figure.facecolor': bg_color,
                'axes.facecolor': bg_color,
                'axes.edgecolor': text_color,
                'axes.labelcolor': text_color,
                'xtick.color': text_color,
                'ytick.color': text_color,
                'text.color': text_color,
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
                'figure.subplot.hspace': 0.6,
                'figure.max_open_warning': 50  
            })

            cursor = self.conn.cursor()

            # Get colors from current theme
            category_colors = self.chart_colors['category_colors']
            bar_colors = self.chart_colors['bar_colors']
            hist_colors = self.chart_colors['hist_colors']
            top_products_colors = self.chart_colors['top_products_colors']

            # Overview tab charts
            overview_left_card, overview_left = self.create_card(
                self.charts_frames['overview'],
                title="Product Distribution",
                icon="📊"
            )
            overview_left_card.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

            overview_right_card, overview_right = self.create_card(
                self.charts_frames['overview'],
                title="Stock Value by Category",
                icon="💰"
            )
            overview_right_card.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

            self.create_product_distribution_chart(overview_left, category_colors)
            self.create_stock_value_chart(overview_right, bar_colors)

            # Products tab charts
            products_left_card, products_left = self.create_card(
                self.charts_frames['products'],
                title="Price Distribution",
                icon="📈"
            )
            products_left_card.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

            products_right_card, products_right = self.create_card(
                self.charts_frames['products'],
                title="Top Products by Value",
                icon="🏆"
            )
            products_right_card.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

            products_bottom_card, products_bottom = self.create_card(
                self.charts_frames['products'],
                title="Quantity Distribution",
                icon="📦"
            )
            products_bottom_card.grid(row=1, column=0, columnspan=2, padx=15, pady=15, sticky="nsew")

            self.create_price_distribution_chart(products_left, hist_colors)
            self.create_top_products_chart(products_right, top_products_colors)
            self.create_quantity_distribution_chart(products_bottom, hist_colors)

            # Categories tab charts
            categories_left_card, categories_left = self.create_card(
                self.charts_frames['categories'],
                title="Products per Category",
                icon="🏷️"
            )
            categories_left_card.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

            categories_right_card, categories_right = self.create_card(
                self.charts_frames['categories'],
                title="Average Price by Category",
                icon="💲"
            )
            categories_right_card.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

            self.create_category_distribution_chart(categories_left, category_colors)
            self.create_avg_price_chart(categories_right, bar_colors)

            # Trends tab charts
            trends_left_card, trends_left = self.create_card(
                self.charts_frames['trends'],
                title="Low Stock Items",
                icon="⚠️"
            )
            trends_left_card.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

            trends_right_card, trends_right = self.create_card(
                self.charts_frames['trends'],
                title="Value Distribution",
                icon="📊"
            )
            trends_right_card.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

            self.create_low_stock_chart(trends_left, bar_colors)
            self.create_value_distribution_chart(trends_right, hist_colors)

            # Final garbage collection
            gc.collect()

        except Exception as e:
            print(f"Error in update_charts: {e}")
            messagebox.showerror("Error", f"Error updating charts: {str(e)}")

    def create_product_distribution_chart(self, parent, colors):
        try:
            fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
            cursor = self.conn.cursor()

            cursor.execute("""
                SELECT c.name, COUNT(p.id) 
                FROM category c 
                LEFT JOIN product p ON c.id = p.id_category 
                GROUP BY c.name
            """)
            cat_data = cursor.fetchall()

            if not cat_data:
                ax.text(0.5, 0.5, 'No data available',
                        ha='center', va='center',
                        fontsize=12, color='gray')
            else:
                categories = [x[0] for x in cat_data]
                counts = [x[1] for x in cat_data]

                # Wrap long category names
                wrapped_labels = ['\n'.join(wrap(label, 15)) for label in categories]

                # Center the pie chart and give more space for labels
                ax.set_position([0.1, 0.1, 0.8, 0.8])

                wedges, texts, autotexts = ax.pie(
                    counts, 
                    labels=wrapped_labels,
                    autopct='%1.0f%%', 
                    colors=colors[:len(categories)], 
                    wedgeprops={'width': 0.6},
                    textprops={'fontsize': 8, 'ha': 'center', 'va': 'center'},
                    pctdistance=0.85,
                    radius=0.8,
                    labeldistance=1.2
                )

                # Lable colors visible in both themes
                plt.setp(autotexts, size=8, weight="bold", color="white")
                plt.setp(texts, size=8, color=self.colors['text'])

                # Add interactive features
                def on_hover(event):
                    for i, wedge in enumerate(wedges):
                        if wedge.contains_point([event.x, event.y]):
                            wedge.set_linewidth(2)
                            wedge.set_edgecolor('black')
                            tooltip = f"{categories[i]}: {counts[i]} products"
                            ax.set_title(tooltip, fontsize=10)
                        else:
                            wedge.set_linewidth(0)
                            wedge.set_edgecolor('none')
                    fig.canvas.draw_idle()

                fig.canvas.mpl_connect('motion_notify_event', on_hover)

            plt.tight_layout(pad=2.0)

            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

            # Сlean garbage to preserve memory
            plt.close(fig)
            gc.collect()

        except Exception as e:
            print(f"Error in create_product_distribution_chart: {e}")
            messagebox.showerror("Error", f"Error creating product distribution chart: {str(e)}")

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

        # Create a text annotation for tooltip that will be updated
        tooltip_text = ax.text(0.5, 0.7, '', transform=ax.transAxes, 
                              ha='center', va='top', fontsize=10,
                              bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.5))
        tooltip_text.set_visible(False)

        
        def on_hover(event):
            if event.inaxes == ax:
                found = False
                for i, bar in enumerate(bars):
                    contains, _ = bar.contains(event)
                    if contains:
                        bar.set_edgecolor('black')
                        bar.set_linewidth(2)
                        tooltip = f"{categories[i]}: {format_value(values[i], None)}"
                        tooltip_text.set_text(tooltip)
                        tooltip_text.set_visible(True)
                        found = True
                    else:
                        bar.set_edgecolor('none')
                        bar.set_linewidth(0)
                
                if not found:
                    tooltip_text.set_visible(False)
                
                fig.canvas.draw_idle()

        # Connect the hover event
        cid = fig.canvas.mpl_connect('motion_notify_event', on_hover)
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        

        canvas.cid = cid

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
        
        # Create a text annotation for tooltip that will be updated
        tooltip_text = ax.text(0.5, 0.95, '', transform=ax.transAxes, 
                              ha='center', va='top', fontsize=10,
                              bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.7))
        tooltip_text.set_visible(False)
        
        # Add interactive features
        def on_hover(event):
            if event.inaxes == ax:
                found = False
                for i, patch in enumerate(patches):
                    contains, _ = patch.contains(event)
                    if contains:
                        patch.set_edgecolor('black')
                        patch.set_linewidth(2)
                        tooltip = f"Price Range: ${bins[i]:.0f} - ${bins[i+1]:.0f}, Count: {int(n[i])}"
                        tooltip_text.set_text(tooltip)
                        tooltip_text.set_visible(True)
                        found = True
                    else:
                        patch.set_edgecolor('white')
                        patch.set_linewidth(1)
                
                if not found:
                    tooltip_text.set_visible(False)
                
                fig.canvas.draw_idle()

        # Connect the hover event
        cid = fig.canvas.mpl_connect('motion_notify_event', on_hover)
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        # Store the connection ID to prevent garbage collection
        canvas.cid = cid

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

        # Add interactive features
        def on_hover(event):
            if event.inaxes == ax:
                for i, bar in enumerate(bars):
                    if bar.contains_point((event.x, event.y)):
                        bar.set_edgecolor('black')
                        tooltip = f"{products[i]}: ${values[i]:,.0f}"
                        ax.set_title(tooltip, fontsize=10)
                    else:
                        bar.set_edgecolor('none')
                fig.canvas.draw_idle()

        fig.canvas.mpl_connect('motion_notify_event', on_hover)
        
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
        
    
        def on_hover(event):
            if event.inaxes == ax:
                for i, patch in enumerate(patches):
                    if patch.contains_point((event.x, event.y), radius=1):
                        patch.set_edgecolor('black')
                        tooltip = f"Quantity Range: {bins[i]:.0f} - {bins[i+1]:.0f}, Count: {int(n[i])}"
                        ax.set_title(tooltip, fontsize=10)
                    else:
                        patch.set_edgecolor('white')
                fig.canvas.draw_idle()

        fig.canvas.mpl_connect('motion_notify_event', on_hover)
        
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

        # Create a text annotation for tooltip that will be updated
        tooltip_text = ax.text(0.5, 0.95, '', transform=ax.transAxes, 
                              ha='center', va='top', fontsize=10,
                              bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.7))
        tooltip_text.set_visible(False)

        # Add interactive features with improved hover detection
        def on_hover(event):
            if event.inaxes == ax:
                found = False
                for i, bar in enumerate(bars):
                    contains, _ = bar.contains(event)
                    if contains:
                        bar.set_edgecolor('black')
                        bar.set_linewidth(2)
                        tooltip = f"{categories[i]}: {counts[i]} products"
                        tooltip_text.set_text(tooltip)
                        tooltip_text.set_visible(True)
                        found = True
                    else:
                        bar.set_edgecolor('none')
                        bar.set_linewidth(0)
                
                if not found:
                    tooltip_text.set_visible(False)
                
                fig.canvas.draw_idle()

        # Connect the hover event
        cid = fig.canvas.mpl_connect('motion_notify_event', on_hover)
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        # Store the connection ID to prevent garbage collection
        canvas.cid = cid

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

        tooltip_text = ax.text(0.5, 0.95, '', transform=ax.transAxes, 
                              ha='center', va='top', fontsize=10,
                              bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.7))
        tooltip_text.set_visible(False)

        def on_hover(event):
            if event.inaxes == ax:
                found = False
                for i, bar in enumerate(bars):
                    contains, _ = bar.contains(event)
                    if contains:
                        bar.set_edgecolor('black')
                        bar.set_linewidth(2)
                        tooltip = f"{categories[i]}: ${avg_prices[i]:.2f}"
                        tooltip_text.set_text(tooltip)
                        tooltip_text.set_visible(True)
                        found = True
                    else:
                        bar.set_edgecolor('none')
                        bar.set_linewidth(0)
                
                if not found:
                    tooltip_text.set_visible(False)
                
                fig.canvas.draw_idle()

    
        cid = fig.canvas.mpl_connect('motion_notify_event', on_hover)
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        canvas.cid = cid

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

            # Create a text annotation for tooltip that will be updated
            tooltip_text = ax.text(0.5, 1, '', transform=ax.transAxes, 
                                  ha='center', va='top', fontsize=10,
                                  bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))
            tooltip_text.set_visible(False)

            def on_hover(event):
                if event.inaxes == ax:
                    found = False
                    for i, bar in enumerate(bars):
                        contains, _ = bar.contains(event)
                        if contains:
                            bar.set_edgecolor('black')
                            bar.set_linewidth(2)
                            tooltip = f"{products[i]}: {quantities[i]} units"
                            tooltip_text.set_text(tooltip)
                            tooltip_text.set_visible(True)
                            found = True
                        else:
                            bar.set_edgecolor('none')
                            bar.set_linewidth(0)
                    
                    if not found:
                        tooltip_text.set_visible(False)
                    
                    fig.canvas.draw_idle()

            cid = fig.canvas.mpl_connect('motion_notify_event', on_hover)

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        # Store the connection ID to prevent garbage collection
        if 'bars' in locals():
            canvas.cid = cid

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
        
        # Create a text annotation for tooltip that will be updated with the current value
        tooltip_text = ax.text(0.5, 0.9, '', transform=ax.transAxes,
                              ha='center', va='top', fontsize=10,
                              bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.7))
        
        def on_hover(event):
            if event.inaxes == ax:
                for i, patch in enumerate(patches):
                    if patch.contains_point((event.x, event.y), radius=1):
                        patch.set_edgecolor('black')
                        tooltip = f"Value Range: ${bins[i]:.0f} - ${bins[i+1]:.0f}, Count: {int(n[i])}"
                        ax.set_title(tooltip_text, fontsize=10)
                    else:
                        patch.set_edgecolor('white')
                fig.canvas.draw_idle()

        fig.canvas.mpl_connect('motion_notify_event', on_hover)
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
    def filter_products(self, *args):
        """Filter products based on search term and advanced filters"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        cursor = self.conn.cursor()
        
        # Build SQL query with filters
        query = """
            SELECT p.id, p.name, p.description, p.price, p.quantity, c.name 
            FROM product p 
            JOIN category c ON p.id_category = c.id
            WHERE 1=1
        """
        
        params = []
        
        search_term = self.search_var.get().lower()
        if search_term:
            query += """ AND (
                LOWER(p.name) LIKE %s OR 
                LOWER(p.description) LIKE %s OR 
                CAST(p.price AS CHAR) LIKE %s OR 
                CAST(p.quantity AS CHAR) LIKE %s OR 
                LOWER(c.name) LIKE %s
            )"""
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern, search_pattern])
        
        # Apply price filters
        query += " AND p.price >= %s AND p.price <= %s"
        params.extend([self.filter_state["price_min"], self.filter_state["price_max"]])
        
        # Apply stock level filters
        query += " AND p.quantity >= %s AND p.quantity <= %s"
        params.extend([self.filter_state["stock_min"], self.filter_state["stock_max"]])
        
        # Apply category filter if categories are selected
        if self.filter_state["categories"]:
            placeholders = ', '.join(['%s'] * len(self.filter_state["categories"]))
            query += f" AND c.name IN ({placeholders})"
            params.extend(self.filter_state["categories"])
        

        cursor.execute(query, params)
        products = cursor.fetchall()
        
        # Display results 
        for i, product in enumerate(products):
            tags = ('evenrow',) if i % 2 == 0 else ('oddrow',)
            self.tree.insert("", "end", values=product, tags=tags)
        
        # Update status
        self.update_filtered_status(len(products), self.get_total_products())

    def update_filtered_status(self, filtered_count, total_count):
    
        # Remove existing status label if any
        if hasattr(self, 'filter_status_label'):
            self.filter_status_label.destroy()
        
        # Only show if we're filtering results
        if self.filter_state["is_active"] or self.search_var.get():
            # Create status label if results are filtered
            status_text = f"Showing {filtered_count} of {total_count} products"
            self.filter_status_label = ctk.CTkLabel(
                self.tree_frame,
                text=status_text,
                font=self.fonts['small'],
                text_color=self.colors['primary']
            )
            self.filter_status_label.pack(side="bottom", anchor="e", padx=10, pady=5)

    def add_product_window(self):
        window = ctk.CTkToplevel(self.root)
        window.title("Add Product")
        window.geometry("500x700")
        window.configure(fg_color=self.colors['card_bg'])
        
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
        
        form_frame = ctk.CTkFrame(window, fg_color=self.colors['card_bg'])
        form_frame.pack(fill="x", padx=40)
        
        self.create_form_field(form_frame, "Product Name:", name_var)
        self.create_form_field(form_frame, "Description:", desc_var)
        self.create_form_field(form_frame, "Price ($):", price_var)
        self.create_form_field(form_frame, "Quantity:", quantity_var)
        
        ctk.CTkLabel(
            form_frame,
            text="Category:",
            font=self.fonts['body'],
            text_color=self.colors['text']
        ).pack(fill="x", pady=(10, 0))
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM category")
        categories = [x[0] for x in cursor.fetchall()]
        
        category_combo = self.create_themed_combobox(
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
            font=self.fonts['body'],
            text_color=self.colors['text']
        ).pack(fill="x", pady=(10, 0))
        
        entry = self.create_themed_entry(
            parent,
            textvariable=variable,
            height=35
        )
        entry.pack(fill="x", pady=(5, 15))
        return entry

    def edit_product_window(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to edit")
            return
            
        values = self.tree.item(selected[0])['values']
        
        window = ctk.CTkToplevel(self.root)
        window.title("Edit Product")
        window.geometry("400x500")
        window.configure(fg_color=self.colors['card_bg'])
        
        name_var = tk.StringVar(value=values[1])
        desc_var = tk.StringVar(value=values[2])
        price_var = tk.StringVar(value=values[3])
        quantity_var = tk.StringVar(value=values[4])
        category_var = tk.StringVar(value=values[5])
        
        form_frame = ctk.CTkFrame(window, fg_color=self.colors['card_bg'])
        form_frame.pack(fill="x", padx=20, pady=10)
        
        # Create form fields
        self.create_form_field(form_frame, "Name:", name_var)
        self.create_form_field(form_frame, "Description:", desc_var)
        self.create_form_field(form_frame, "Price:", price_var)
        self.create_form_field(form_frame, "Quantity:", quantity_var)
        
        ctk.CTkLabel(
            form_frame,
            text="Category:",
            font=self.fonts['body'],
            text_color=self.colors['text']
        ).pack(fill="x", pady=(10, 0))
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM category")
        categories = [x[0] for x in cursor.fetchall()]
        
        category_combo = self.create_themed_combobox(
            form_frame,
            variable=category_var,
            values=categories,
            height=35
        )
        category_combo.pack(fill="x", pady=(5, 15))
        
        def save_changes():
            try:
                cursor = self.conn.cursor()
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
                
        ctk.CTkButton(
            form_frame,
            text="Save Changes",
            command=save_changes,
            fg_color=self.colors['success'],
            hover_color=self.colors['success']
        ).pack(pady=20)
        
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
        window.configure(fg_color=self.colors['card_bg'])
        
        ctk.CTkLabel(
            window,
            text="Add New Category",
            font=self.fonts['heading'],
            text_color=self.colors['text']
        ).pack(pady=(20, 30))
        
        name_var = tk.StringVar()
        
        form_frame = ctk.CTkFrame(window, fg_color=self.colors['card_bg'])
        form_frame.pack(fill="x", padx=40)
        
        self.create_form_field(form_frame, "Category Name:", name_var)
        
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
        window.configure(fg_color=self.colors['card_bg'])
        
        ctk.CTkLabel(
            window,
            text="Delete Category",
            font=self.fonts['heading'],
            text_color=self.colors['text']
        ).pack(pady=(20, 30))
        
        category_var = tk.StringVar()
        
        form_frame = ctk.CTkFrame(window, fg_color=self.colors['card_bg'])
        form_frame.pack(fill="x", padx=40)
        
        ctk.CTkLabel(
            form_frame,
            text="Select Category to Delete:",
            font=self.fonts['body'],
            text_color=self.colors['text']
        ).pack(fill="x", pady=(10, 0))
        
        category_combo = self.create_themed_combobox(
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
            cursor = self.conn.cursor()
            
            # Start with base query
            query = """
                    SELECT p.id, p.name, p.description, p.price, p.quantity, c.name as category
                    FROM product p 
                    JOIN category c ON p.id_category = c.id
                WHERE 1=1
            """
            
            params = []
            
            # Add search term filter if there are filters applied
            search_term = self.search_var.get().lower()
            if search_term:
                query += """ AND (
                    LOWER(p.name) LIKE %s OR 
                    LOWER(p.description) LIKE %s OR 
                    CAST(p.price AS CHAR) LIKE %s OR 
                    CAST(p.quantity AS CHAR) LIKE %s OR 
                    LOWER(c.name) LIKE %s
                )"""
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern, search_pattern, search_pattern, search_pattern])
            
            # Apply filters
            if self.filter_state["is_active"]:
                query += " AND p.price >= %s AND p.price <= %s"
                params.extend([self.filter_state["price_min"], self.filter_state["price_max"]])
                
                
                query += " AND p.quantity >= %s AND p.quantity <= %s"
                params.extend([self.filter_state["stock_min"], self.filter_state["stock_max"]])
                
                
                if self.filter_state["categories"]:
                    placeholders = ', '.join(['%s'] * len(self.filter_state["categories"]))
                    query += f" AND c.name IN ({placeholders})"
                    params.extend(self.filter_state["categories"])
            
            # Apply current sorting
            column_map = {
                "ID": "p.id",
                "Name": "p.name",
                "Description": "p.description",
                "Price": "p.price",
                "Quantity": "p.quantity",
                "Category": "c.name"
            }
            
            if hasattr(self, 'sort_column') and self.sort_column:
                query += f" ORDER BY {column_map[self.sort_column]}"
                if hasattr(self, 'sort_reverse') and self.sort_reverse:
                    query += " DESC"
            
    
            cursor.execute(query, params)
            data = cursor.fetchall()
            
            # Create DataFrame with the filtered data
            columns = ['ID', 'Name', 'Description', 'Price', 'Quantity', 'Category']
            df = pd.DataFrame(data, columns=columns)
            
            # Create data-csv directory if it doesn't exist
            export_dir = os.path.join("data-csv")
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            
            # Generate filename with timestamp and filter indication in the file's title
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filter_indicator = "_filtered" if (self.filter_state["is_active"] or search_term) else ""
            filename = f"products{filter_indicator}_{timestamp}.csv"
            full_path = os.path.join(export_dir, filename)
            
            # Export to CSV
            df.to_csv(full_path, index=False)
            
            # Show success message 
            if self.filter_state["is_active"] or search_term:
                filter_desc = []
                if search_term:
                    filter_desc.append(f"Search: '{search_term}'")
                if self.filter_state["is_active"]:
                    if self.filter_state["price_min"] > 0 or self.filter_state["price_max"] < 10000:
                        filter_desc.append(f"Price: ${self.filter_state['price_min']} - ${self.filter_state['price_max']}")
                    if self.filter_state["stock_min"] > 0 or self.filter_state["stock_max"] < 1000:
                        filter_desc.append(f"Stock: {self.filter_state['stock_min']} - {self.filter_state['stock_max']}")
                    if self.filter_state["categories"]:
                        filter_desc.append(f"Categories: {', '.join(self.filter_state['categories'])}")
                
                message = f"Filtered data exported successfully to {filename}\nApplied filters: {'; '.join(filter_desc)}"
            else:
                message = f"All data exported successfully to {filename}"
            
            messagebox.showinfo("Success", message)
            
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
            fg_color=self.colors['card_bg'],
            corner_radius=10,
            border_width=1,
            border_color=self.colors['card_border']
        )
        
        if width:
            outer_frame.configure(width=width)
        if height:
            outer_frame.configure(height=height)
            outer_frame.pack_propagate(False)
        
        if title:
            title_frame = ctk.CTkFrame(
                outer_frame,
                fg_color=self.colors['hover'], 
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
        
        content_frame = ctk.CTkFrame(outer_frame, fg_color=self.colors['card_bg'])
        content_frame.pack(fill="both", expand=True, padx=15, pady=(0 if title else 15, 10))  
        
        return outer_frame, content_frame

    def run(self):
        self.root.mainloop()

    def init_filter_state(self):
        # Initiliaze filter state 
        self.filter_state = {
            "price_min": 0,        
            "price_max": 10000,    
            "stock_min": 0,        
            "stock_max": 1000,     
            "categories": [],      
            "date_min": None,      
            "date_max": None,      
            "is_active": False     
        }

    def show_advanced_filters(self):
        # Create a toplevel window for advanced filters
        filter_window = ctk.CTkToplevel(self.root)
        filter_window.title("Advanced Filters")
        filter_window.geometry("600x500")
        filter_window.configure(fg_color=self.colors['card_bg'])
        
        filter_window.transient(self.root)
        filter_window.grab_set()
        
        # Add a title
        ctk.CTkLabel(
            filter_window,
            text="Advanced Filters",
            font=self.fonts['heading'],
            text_color=self.colors['text']
        ).pack(pady=(20, 30))
        
        content_frame = ctk.CTkFrame(filter_window, fg_color=self.colors['card_bg'])
        content_frame.pack(fill="both", expand=True, padx=30, pady=0)
        
        price_frame = ctk.CTkFrame(content_frame, fg_color=self.colors['card_bg'])
        price_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            price_frame,
            text="Price Range ($):",
            font=self.fonts['body'],
            text_color=self.colors['text']
        ).pack(side="left", padx=(0, 10))
        
        price_min_var = tk.StringVar(value=str(self.filter_state["price_min"]))
        price_min_entry = self.create_themed_entry(
            price_frame,
            textvariable=price_min_var,
            width=80,
            height=30
        )
        price_min_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(
            price_frame,
            text="to",
            font=self.fonts['body'],
            text_color=self.colors['text']
        ).pack(side="left", padx=5)
        
        price_max_var = tk.StringVar(value=str(self.filter_state["price_max"]))
        price_max_entry = self.create_themed_entry(
            price_frame,
            textvariable=price_max_var,
            width=80,
            height=30
        )
        price_max_entry.pack(side="left", padx=5)
        
        stock_frame = ctk.CTkFrame(content_frame, fg_color=self.colors['card_bg'])
        stock_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            stock_frame,
            text="Stock Level:",
            font=self.fonts['body'],
            text_color=self.colors['text']
        ).pack(side="left", padx=(0, 10))
        
        stock_min_var = tk.StringVar(value=str(self.filter_state["stock_min"]))
        stock_min_entry = self.create_themed_entry(
            stock_frame,
            textvariable=stock_min_var,
            width=80,
            height=30
        )
        stock_min_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(
            stock_frame,
            text="to",
            font=self.fonts['body'],
            text_color=self.colors['text']
        ).pack(side="left", padx=5)
        
        stock_max_var = tk.StringVar(value=str(self.filter_state["stock_max"]))
        stock_max_entry = self.create_themed_entry(
            stock_frame,
            textvariable=stock_max_var,
            width=80,
            height=30
        )
        stock_max_entry.pack(side="left", padx=5)
        
        category_frame = ctk.CTkFrame(content_frame, fg_color=self.colors['card_bg'])
        category_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            category_frame,
            text="Categories:",
            font=self.fonts['body'],
            text_color=self.colors['text']
        ).pack(anchor="w", pady=(0, 5))
        
        # Get all categories
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM category")
        categories = [cat[0] for cat in cursor.fetchall()]
        
        # Category checkboxes
        category_vars = {}
        checkbox_frame = ctk.CTkFrame(category_frame, fg_color=self.colors['card_bg'])
        checkbox_frame.pack(fill="x", padx=20)
        
        for i, category in enumerate(categories):
            var = tk.BooleanVar(value=category in self.filter_state["categories"])
            category_vars[category] = var
            
            checkbox = ctk.CTkCheckBox(
                checkbox_frame,
                text=category,
                variable=var,
                font=self.fonts['body'],
                text_color=self.colors['text'],
                fg_color=self.colors['primary'],
                hover_color=self.colors['secondary'],
                border_color=self.colors['primary']
            )
            checkbox.grid(row=i//2, column=i%2, sticky="w", padx=10, pady=5)
        
        # Reset and Apply buttons
        button_frame = ctk.CTkFrame(filter_window, fg_color=self.colors['card_bg'])
        button_frame.pack(fill="x", pady=20, padx=30)
        
        def reset_filters():
            self.init_filter_state()
            self.update_filter_indicator()
            filter_window.destroy()
            self.filter_products()
        
        def apply_filters():
            try:
                # Update filter state with new values
                price_min = float(price_min_var.get())
                price_max = float(price_max_var.get())
                stock_min = int(stock_min_var.get())
                stock_max = int(stock_max_var.get())
                
                # Store values in filter state
                self.filter_state["price_min"] = price_min
                self.filter_state["price_max"] = price_max
                self.filter_state["stock_min"] = stock_min
                self.filter_state["stock_max"] = stock_max
                
                # Update categories
                self.filter_state["categories"] = [cat for cat, var in category_vars.items() if var.get()]
                
                # Set filter as active if any non-default filter is applied
                self.filter_state["is_active"] = (
                    price_min > 0 or
                    price_max < 10000 or
                    stock_min > 0 or
                    stock_max < 1000 or
                    len(self.filter_state["categories"]) > 0
                )
                
                # Update the filter button appearance to display active filters
                self.update_filter_indicator()
                
                filter_window.destroy()
                
                # Apply the filters with current search term
                self.filter_products()
                
                if self.filter_state["is_active"]:
                    filter_desc = []
                    
                    if price_min > 0 or price_max < 10000:
                        filter_desc.append(f"Price: ${price_min} - ${price_max}")
                    
                    if stock_min > 0 or stock_max < 1000:
                        filter_desc.append(f"Stock: {stock_min} - {stock_max}")
                    
                    if self.filter_state["categories"]:
                        filter_desc.append(f"Categories: {', '.join(self.filter_state['categories'])}")
                    
                    messagebox.showinfo("Filters Applied", 
                        f"Filters applied successfully.\n{'; '.join(filter_desc)}")
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for price and stock levels")
        
        reset_btn = ctk.CTkButton(
            button_frame,
            text="Reset",
            command=reset_filters,
            fg_color=self.colors['card_bg'],
            hover_color=self.colors['hover'],
            border_width=1,
            border_color=self.colors['primary'],
            text_color=self.colors['text'],
            width=120,
            height=35
        )
        reset_btn.pack(side="left", padx=10)
        
        apply_btn = ctk.CTkButton(
            button_frame,
            text="Apply Filters",
            command=apply_filters,
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary'],
            width=120,
            height=35
        )
        apply_btn.pack(side="right", padx=10)

    def update_filter_indicator(self):
        # Update the filter button appearance based on active filters
        if self.filter_state["is_active"]:
            # Count active filters for better indication
            active_filters = 0
            
            # Check price filters
            if self.filter_state["price_min"] > 0 or self.filter_state["price_max"] < 10000:
                active_filters += 1
                
            # Check stock filters
            if self.filter_state["stock_min"] > 0 or self.filter_state["stock_max"] < 1000:
                active_filters += 1
                
            # Check category filters
            if self.filter_state["categories"]:
                active_filters += 1
            
            # Visual indication of the active filters
            filter_text = f"Filters ({active_filters})"
            
            self.advanced_filters_btn.configure(
                text=filter_text,
                fg_color=self.colors['success'],
                hover_color="#057857" 
            )
        else:
            self.advanced_filters_btn.configure(
                text="Filters",
                fg_color=self.colors['primary'],
                hover_color=self.colors['secondary']
            )

if __name__ == "__main__":
    app = StockManager()
    app.run()