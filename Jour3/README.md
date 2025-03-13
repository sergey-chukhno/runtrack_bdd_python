# Stock Management System

A beautiful and professional stock management system built with Python and MySQL. This application provides a modern graphical interface for managing product inventory, with features including product management, category filtering, data visualization, and CSV export capabilities.

## Features

- Modern dark-themed GUI using CustomTkinter
- Product management (Add, Edit, Delete)
- Category-based filtering
- Real-time data visualization with charts
- CSV export functionality (all products or filtered by category)
- Beautiful dashboard with product statistics

## Prerequisites

- Python 3.8 or higher
- MySQL Server
- pip (Python package installer)

## Installation

1. Clone this repository or download the source code

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure MySQL:
   - Make sure MySQL server is running
   - Update the MySQL connection details in `stock_manager.py` if needed:
     ```python
     self.conn = mysql.connector.connect(
         host="localhost",
         user="root",
         password=""  # Replace with your MySQL password
     )
     ```

## Usage

1. Run the application:
```bash
python stock_manager.py
```

2. The application will automatically:
   - Create the database if it doesn't exist
   - Create required tables
   - Insert sample categories and products if tables are empty

3. Main features:
   - View all products in the main table
   - Add new products using the "Add Product" button
   - Edit existing products by selecting them and clicking "Edit Product"
   - Delete products by selecting them and clicking "Delete Product"
   - Filter products by category using the dropdown
   - Export all products or filtered products to CSV
   - View real-time statistics in the charts section

## Data Visualization

The application includes two charts:
1. Pie chart showing the distribution of products across categories
2. Bar chart showing the total stock value by category

These charts update automatically when products are added, edited, or deleted.

## Database Schema

### Category Table
- id (INT, Primary Key, Auto-increment)
- name (VARCHAR(255))

### Product Table
- id (INT, Primary Key, Auto-increment)
- name (VARCHAR(255))
- description (TEXT)
- price (INT)
- quantity (INT)
- id_category (INT, Foreign Key referencing category.id)

## Contributing

Feel free to submit issues and enhancement requests! 