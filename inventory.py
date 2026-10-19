"""
inventory.py - Inventory Management and Data Persistence Module
================================================================
This module handles all inventory operations:
- Loading and saving products to local JSON storage
- Validating product fields (non-negative numbers, unique IDs, non-empty text)
- CRUD operations (Create, Read, Update, Delete)
- Search and filtering utilities
"""

import json
import os
import sys
from typing import List, Dict, Any, Optional, Tuple

# Ensure UTF-8 output on Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "inventory.json")

# Fallback default inventory in case the JSON file is missing or corrupted
DEFAULT_PRODUCTS: List[Dict[str, Any]] = [
    {
        "product_id": "P001",
        "name": "Organic Whole Milk (1 Gallon)",
        "category": "Groceries",
        "purchase_cost": 180.00,
        "selling_price": 240.00,
        "stock": 18,
        "min_stock": 15,
        "monthly_sales": 65
    },
    {
        "product_id": "P002",
        "name": "Arabica Coffee Beans (1 lb)",
        "category": "Groceries",
        "purchase_cost": 420.00,
        "selling_price": 699.00,
        "stock": 25,
        "min_stock": 10,
        "monthly_sales": 42
    },
    {
        "product_id": "P003",
        "name": "Artisan Sourdough Bread",
        "category": "Groceries",
        "purchase_cost": 65.00,
        "selling_price": 120.00,
        "stock": 0,
        "min_stock": 12,
        "monthly_sales": 38
    },
    {
        "product_id": "P004",
        "name": "Wireless Ergonomic Mouse",
        "category": "Electronics",
        "purchase_cost": 450.00,
        "selling_price": 899.00,
        "stock": 4,
        "min_stock": 10,
        "monthly_sales": 10
    },
    {
        "product_id": "P005",
        "name": "USB-C Fast Charger 65W",
        "category": "Electronics",
        "purchase_cost": 650.00,
        "selling_price": 1299.00,
        "stock": 35,
        "min_stock": 12,
        "monthly_sales": 55
    },
    {
        "product_id": "P006",
        "name": "Noise-Cancelling Headphones",
        "category": "Electronics",
        "purchase_cost": 2200.00,
        "selling_price": 3999.00,
        "stock": 22,
        "min_stock": 6,
        "monthly_sales": 3
    },
    {
        "product_id": "P007",
        "name": "Men's Cotton Crew T-Shirt",
        "category": "Clothing",
        "purchase_cost": 250.00,
        "selling_price": 499.00,
        "stock": 28,
        "min_stock": 10,
        "monthly_sales": 20
    },
    {
        "product_id": "P008",
        "name": "Vintage Denim Casual Jacket",
        "category": "Clothing",
        "purchase_cost": 1100.00,
        "selling_price": 2199.00,
        "stock": 19,
        "min_stock": 5,
        "monthly_sales": 2
    },
    {
        "product_id": "P009",
        "name": "Running Sports Socks (3-Pack)",
        "category": "Clothing",
        "purchase_cost": 120.00,
        "selling_price": 299.00,
        "stock": 40,
        "min_stock": 15,
        "monthly_sales": 35
    },
    {
        "product_id": "P010",
        "name": "Herbal Aloe Shampoo 500ml",
        "category": "Personal Care",
        "purchase_cost": 140.00,
        "selling_price": 249.00,
        "stock": 16,
        "min_stock": 10,
        "monthly_sales": 18
    },
    {
        "product_id": "P011",
        "name": "Electric Toothbrush Heads (4-Pack)",
        "category": "Personal Care",
        "purchase_cost": 350.00,
        "selling_price": 749.00,
        "stock": 3,
        "min_stock": 8,
        "monthly_sales": 22
    },
    {
        "product_id": "P012",
        "name": "Clearance Travel Sunscreen SPF 50",
        "category": "Personal Care",
        "purchase_cost": 299.00,
        "selling_price": 199.00,
        "stock": 14,
        "min_stock": 5,
        "monthly_sales": 6
    }
]


def format_currency(amount: float) -> str:
    """
    Format numeric monetary amount into Indian Rupee (INR) currency string.
    Example: format_currency(1499) -> '₹1,499.00'
    """
    return f"₹{float(amount):,.2f}"


def validate_product_data(
    data: Dict[str, Any],
    existing_ids: Optional[List[str]] = None,
    is_new: bool = True
) -> Tuple[bool, str]:
    """
    Validate product fields against business rules:
    - product_id must be non-empty and unique (if is_new)
    - name and category must be non-empty strings
    - purchase_cost and selling_price must be non-negative floats
    - stock, min_stock, and monthly_sales must be non-negative integers
    """
    if not isinstance(data, dict):
        return False, "Product record must be a dictionary."

    # Validate Product ID
    product_id = str(data.get("product_id", "")).strip()
    if not product_id:
        return False, "Product ID cannot be empty."
    if is_new and existing_ids and product_id in existing_ids:
        return False, f"Product ID '{product_id}' already exists."

    # Validate Name
    name = str(data.get("name", "")).strip()
    if not name:
        return False, "Product name cannot be empty."

    # Validate Category
    category = str(data.get("category", "")).strip()
    if not category:
        return False, "Category cannot be empty."

    # Validate Purchase Cost
    try:
        purchase_cost = float(data.get("purchase_cost", 0.0))
        if purchase_cost < 0:
            return False, "Purchase cost cannot be negative."
    except (ValueError, TypeError):
        return False, "Purchase cost must be a valid number."

    # Validate Selling Price
    try:
        selling_price = float(data.get("selling_price", 0.0))
        if selling_price < 0:
            return False, "Selling price cannot be negative."
    except (ValueError, TypeError):
        return False, "Selling price must be a valid number."

    # Validate Stock Quantity
    try:
        stock = int(data.get("stock", 0))
        if stock < 0:
            return False, "Available stock cannot be negative."
    except (ValueError, TypeError):
        return False, "Stock must be a valid non-negative integer."

    # Validate Minimum Stock Threshold
    try:
        min_stock = int(data.get("min_stock", 0))
        if min_stock < 0:
            return False, "Minimum stock threshold cannot be negative."
    except (ValueError, TypeError):
        return False, "Minimum stock must be a valid non-negative integer."

    # Validate Monthly Sales
    try:
        monthly_sales = int(data.get("monthly_sales", 0))
        if monthly_sales < 0:
            return False, "Monthly sales quantity cannot be negative."
    except (ValueError, TypeError):
        return False, "Monthly sales must be a valid non-negative integer."

    return True, "Valid"


def load_inventory(file_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Safely load inventory from the JSON file.
    If the file does not exist or contains invalid JSON, restores default inventory.
    """
    path = file_path or DEFAULT_DATA_PATH

    if not os.path.exists(path):
        # Create directory and save defaults
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        save_inventory(DEFAULT_PRODUCTS, path)
        return [dict(p) for p in DEFAULT_PRODUCTS]

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                # Basic check for dict records
                valid_records = []
                for item in data:
                    if isinstance(item, dict) and "product_id" in item:
                        valid_records.append(item)
                if valid_records:
                    return valid_records
        # If file was empty or corrupted list
        save_inventory(DEFAULT_PRODUCTS, path)
        return [dict(p) for p in DEFAULT_PRODUCTS]
    except (json.JSONDecodeError, IOError, OSError):
        # Fallback to default products on error
        save_inventory(DEFAULT_PRODUCTS, path)
        return [dict(p) for p in DEFAULT_PRODUCTS]


def save_inventory(inventory: List[Dict[str, Any]], file_path: Optional[str] = None) -> bool:
    """
    Safely save the inventory list to the local JSON file.
    """
    path = file_path or DEFAULT_DATA_PATH
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(inventory, f, indent=2)
        return True
    except (IOError, OSError):
        return False


def get_product_by_id(inventory: List[Dict[str, Any]], product_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a single product by its unique Product ID (case-insensitive)."""
    pid = product_id.strip().upper()
    for product in inventory:
        if str(product.get("product_id", "")).strip().upper() == pid:
            return product
    return None


def search_products(inventory: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """
    Search for products matching the query by Product ID, Name, or Category.
    Case-insensitive substring match.
    """
    q = query.strip().lower()
    if not q:
        return inventory

    results = []
    for product in inventory:
        pid = str(product.get("product_id", "")).lower()
        name = str(product.get("name", "")).lower()
        cat = str(product.get("category", "")).lower()
        if q in pid or q in name or q in cat:
            results.append(product)
    return results


def add_product(
    inventory: List[Dict[str, Any]],
    product_data: Dict[str, Any],
    file_path: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Validate and add a new product to inventory, persisting changes to JSON.
    """
    existing_ids = [str(p.get("product_id", "")).strip().upper() for p in inventory]
    pid = str(product_data.get("product_id", "")).strip().upper()

    if pid in existing_ids:
        return False, f"Duplicate product ID '{pid}'. Product IDs must be unique."

    is_valid, msg = validate_product_data(product_data, existing_ids=existing_ids, is_new=True)
    if not is_valid:
        return False, msg

    # Normalize fields
    clean_product = {
        "product_id": pid,
        "name": str(product_data["name"]).strip(),
        "category": str(product_data["category"]).strip(),
        "purchase_cost": round(float(product_data["purchase_cost"]), 2),
        "selling_price": round(float(product_data["selling_price"]), 2),
        "stock": int(product_data["stock"]),
        "min_stock": int(product_data["min_stock"]),
        "monthly_sales": int(product_data["monthly_sales"]),
    }

    inventory.append(clean_product)
    saved = save_inventory(inventory, file_path)
    if not saved:
        return False, "Product was added to memory but could not be saved to disk."
    return True, f"Product '{clean_product['name']}' (ID: {pid}) added successfully."


def update_stock(
    inventory: List[Dict[str, Any]],
    product_id: str,
    quantity: int,
    mode: str = "set",
    file_path: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Update stock for a specific product.
    mode can be 'set' (override current stock) or 'delta' (add/subtract units).
    Stock quantity cannot become negative.
    """
    product = get_product_by_id(inventory, product_id)
    if not product:
        return False, f"Product with ID '{product_id}' not found."

    current_stock = int(product.get("stock", 0))

    if mode == "set":
        if quantity < 0:
            return False, "Stock quantity cannot be negative."
        new_stock = quantity
    elif mode == "delta":
        new_stock = current_stock + quantity
        if new_stock < 0:
            return False, f"Cannot reduce stock below 0. Current: {current_stock}, Adjustment: {quantity}."
    else:
        return False, f"Invalid update mode '{mode}'. Use 'set' or 'delta'."

    product["stock"] = new_stock
    save_inventory(inventory, file_path)
    return True, f"Stock for '{product['name']}' updated to {new_stock} units."


def delete_product(
    inventory: List[Dict[str, Any]],
    product_id: str,
    file_path: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Remove a product from inventory after confirmation.
    """
    product = get_product_by_id(inventory, product_id)
    if not product:
        return False, f"Product with ID '{product_id}' not found."

    inventory.remove(product)
    save_inventory(inventory, file_path)
    return True, f"Product '{product['name']}' ({product_id}) removed from inventory."


def get_categories(inventory: List[Dict[str, Any]]) -> List[str]:
    """Return a sorted list of unique categories in inventory."""
    categories = sorted(list(set(str(p.get("category", "General")).strip() for p in inventory)))
    return categories


def calculate_profit(product: Dict[str, Any]) -> float:
    """Calculate profit per unit: Selling price - Purchase cost."""
    selling = float(product.get("selling_price", 0.0))
    cost = float(product.get("purchase_cost", 0.0))
    return round(selling - cost, 2)


def calculate_profit_margin(product: Dict[str, Any]) -> float:
    """
    Calculate profit margin percentage:
    Profit margin % = ((Selling price - Purchase cost) / Selling price) * 100
    Safely handles zero or negative selling prices.
    """
    selling = float(product.get("selling_price", 0.0))
    cost = float(product.get("purchase_cost", 0.0))
    if selling <= 0:
        return 0.0
    margin = ((selling - cost) / selling) * 100.0
    return round(margin, 2)
