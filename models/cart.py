from models.product import Product


class CartItem:
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity

    @property
    def subtotal(self):
        return self.product.price * self.quantity


class Cart:
    def __init__(self):
        self._items = []

    def add_item(self, product, quantity):
        if not product.is_available(quantity):
            raise ValueError(f"Only {product.stock} unit(s) of '{product.name}' in stock")
        # Merge if product already in cart
        for item in self._items:
            if item.product.product_id == product.product_id:
                new_qty = item.quantity + quantity
                if not product.is_available(new_qty):
                    raise ValueError(f"Cannot add {quantity} more. Only {product.stock} in stock")
                item.quantity = new_qty
                return
        self._items.append(CartItem(product, quantity))

    def remove_item(self, product_id):
        self._items = [i for i in self._items if i.product.product_id != product_id]

    def clear(self):
        self._items.clear()

    @property
    def items(self):
        return self._items

    @property
    def total(self):
        return sum(item.subtotal for item in self._items)

    def is_empty(self):
        return len(self._items) == 0
