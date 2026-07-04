import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
ORDERS_FILE   = os.path.join(DATA_DIR, "orders.json")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


# ── Products ─────────────────────────────────────────────────────────────────

def load_products():
    """Return list of product dicts from JSON, or None if file missing."""
    if not os.path.exists(PRODUCTS_FILE):
        return None
    with open(PRODUCTS_FILE, "r") as f:
        return json.load(f)


def save_products(products):
    """Persist a list of Product objects to JSON."""
    _ensure_data_dir()
    data = [
        {
            "product_id": p.product_id,
            "name":       p.name,
            "price":      p.price,
            "stock":      p.stock,
        }
        for p in products
    ]
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ── Orders ────────────────────────────────────────────────────────────────────

def save_order(order):
    """Append a completed Order to the orders JSON file."""
    _ensure_data_dir()
    history = []
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r") as f:
            history = json.load(f)

    history.append({
        "order_id":  order.order_id,
        "timestamp": order.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "items": [
            {
                "product_id": item.product.product_id,
                "name":       item.product.name,
                "price":      item.product.price,
                "quantity":   item.quantity,
                "subtotal":   item.subtotal,
            }
            for item in order.items
        ],
        "subtotal": order.subtotal,
        "tax":      order.tax,
        "total":    order.total,
    })

    with open(ORDERS_FILE, "w") as f:
        json.dump(history, f, indent=2)


def load_orders():
    """Return all saved orders as a list of dicts, or empty list if none."""
    if not os.path.exists(ORDERS_FILE):
        return []
    with open(ORDERS_FILE, "r") as f:
        return json.load(f)
