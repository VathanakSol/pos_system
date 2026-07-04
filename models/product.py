class Product:
    def __init__(self, product_id, name, price, stock):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock

    def is_available(self, quantity=1):
        return self.stock >= quantity

    def reduce_stock(self, quantity):
        if not self.is_available(quantity):
            raise ValueError(f"Insufficient stock for '{self.name}'")
        self.stock -= quantity

    def __repr__(self):
        return f"[{self.product_id}] {self.name} - ${self.price:.2f} (Stock: {self.stock})"
