from models.product import Product
from services.storage import load_products, save_products


class Inventory:
    def __init__(self):
        self._products = {}
        self._load()

    def _load(self):
        """Load from JSON if it exists, otherwise seed defaults."""
        data = load_products()
        if data:
            for d in data:
                p = Product(d["product_id"], d["name"], d["price"], d["stock"])
                self._products[p.product_id] = p
        else:
            self._seed_products()
            self._save()

    def _save(self):
        save_products(self.get_all())

    def _seed_products(self):
        defaults = [
            Product(1, "Apple",         0.50, 100),
            Product(2, "Banana",        0.30, 150),
            Product(3, "Milk (1L)",     1.20,  50),
            Product(4, "Bread",         2.50,  40),
            Product(5, "Eggs (12pk)",   3.00,  30),
            Product(6, "Cheese",        4.50,  20),
            Product(7, "Water (500ml)", 0.80, 200),
            Product(8, "Coffee",        6.00,  25),
        ]
        for p in defaults:
            self._products[p.product_id] = p

    def get_all(self):
        return list(self._products.values())

    def find_by_id(self, product_id):
        return self._products.get(product_id)

    def add_product(self, product):
        if product.product_id in self._products:
            raise ValueError(f"Product ID {product.product_id} already exists")
        self._products[product.product_id] = product
        self._save()

    def sync(self):
        """Call after stock changes to persist updated inventory."""
        self._save()

    def next_id(self):
        return max(self._products.keys(), default=0) + 1
