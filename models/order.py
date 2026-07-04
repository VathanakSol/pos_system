from datetime import datetime
from services.storage import load_orders


class Order:
    _counter = None  # lazily initialized from persisted orders

    @classmethod
    def _init_counter(cls):
        orders = load_orders()
        if orders:
            cls._counter = max(o["order_id"] for o in orders)
        else:
            cls._counter = 1000

    def __init__(self, cart, tax_rate=0.08):
        if Order._counter is None:
            Order._init_counter()
        Order._counter += 1
        self.order_id = Order._counter
        self.items = list(cart.items)
        self.tax_rate = tax_rate
        self.subtotal = cart.total
        self.tax = round(self.subtotal * tax_rate, 2)
        self.total = round(self.subtotal + self.tax, 2)
        self.timestamp = datetime.now()
