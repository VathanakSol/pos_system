from models.order import Order
from services.storage import save_order


class CheckoutService:
    TAX_RATE = 0.08

    def process(self, cart, inventory):
        if cart.is_empty():
            raise ValueError("Cannot checkout an empty cart")

        # Deduct stock for each item
        for item in cart.items:
            item.product.reduce_stock(item.quantity)

        order = Order(cart, self.TAX_RATE)

        # Persist order and updated stock
        save_order(order)
        inventory.sync()

        cart.clear()
        return order
