import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from models.product import Product
from models.cart import Cart
from services.inventory import Inventory
from services.checkout import CheckoutService
from services.auth import AuthService
from services.storage import load_orders
from utils.receipt import ReceiptPrinter
from utils.ui import (
    clear, typewrite, spinner, progress_bar,
    flash_message, banner, section, divider, make_table, console
)

console = Console()


class POSApp:
    def __init__(self):
        self.inventory        = Inventory()
        self.cart             = Cart()
        self.checkout_service = CheckoutService()
        self.receipt_printer  = ReceiptPrinter()
        self.auth_service     = AuthService()
        self.current_user     = None

    # ── Auth ──────────────────────────────────────────────────────────────────

    def _login(self):
        banner()
        typewrite("  Welcome! Please log in to continue.", delay=0.02)
        console.print()
        for attempt in range(3):
            username = input("  Username: ").strip()
            password = input("  Password: ").strip()
            spinner("Verifying credentials...", duration=0.8)
            user = self.auth_service.login(username, password)
            if user:
                self.current_user = user
                flash_message(f"✔  Login successful! Welcome, {user.username} [{user.role}]", "green")
                spinner("Loading system...", duration=1.0)
                clear()
                return True
            remaining = 2 - attempt
            flash_message(f"✘  Invalid credentials. {remaining} attempt(s) left.", "red")
            console.print()
        flash_message("✘  Too many failed attempts. Exiting.", "red")
        return False

    def _logout(self):
        flash_message(f"  Goodbye, {self.current_user.username}!", "yellow")
        self.current_user = None
        self.cart.clear()

    # ── Menus ─────────────────────────────────────────────────────────────────

    def _show_cashier_menu(self):
        clear()
        items = [
            ("[bold cyan]1[/bold cyan]", "View Products"),
            ("[bold cyan]2[/bold cyan]", "Add to Cart"),
            ("[bold cyan]3[/bold cyan]", "View Cart"),
            ("[bold cyan]4[/bold cyan]", "Remove from Cart"),
            ("[bold cyan]5[/bold cyan]", "Checkout"),
            ("[bold red]0[/bold red]",   "Logout"),
        ]
        menu_text = "\n".join(f"  [ {k} ]  {v}" for k, v in items)
        console.print(Panel(
            menu_text,
            title=f"[bold white]CASHIER · {self.current_user.username}[/bold white]",
            border_style="cyan", padding=(1, 2)
        ))

    def _show_manager_menu(self):
        clear()
        items = [
            ("[bold cyan]1[/bold cyan]", "View Products"),
            ("[bold cyan]2[/bold cyan]", "Add to Cart"),
            ("[bold cyan]3[/bold cyan]", "View Cart"),
            ("[bold cyan]4[/bold cyan]", "Remove from Cart"),
            ("[bold cyan]5[/bold cyan]", "Checkout"),
            ("[bold cyan]6[/bold cyan]", "Add New Product"),
            ("[bold cyan]7[/bold cyan]", "Transaction History"),
            ("[bold cyan]8[/bold cyan]", "Manage Users"),
            ("[bold red]0[/bold red]",   "Logout"),
        ]
        menu_text = "\n".join(f"  [ {k} ]  {v}" for k, v in items)
        console.print(Panel(
            menu_text,
            title=f"[bold white]MANAGER · {self.current_user.username}[/bold white]",
            border_style="yellow", padding=(1, 2)
        ))

    # ── Shared actions ────────────────────────────────────────────────────────

    def _show_products(self):
        section("PRODUCTS")
        table = make_table(
            {"header": "ID",      "justify": "right",  "style": "dim",          "min_width": 4},
            {"header": "Name",    "justify": "left",   "style": "white",         "min_width": 20},
            {"header": "Price",   "justify": "right",  "style": "cyan"},
            {"header": "Stock",   "justify": "right",  "style": "green"},
        )
        for p in self.inventory.get_all():
            stock_style = "red" if p.stock < 10 else "green"
            table.add_row(
                str(p.product_id),
                p.name,
                f"${p.price:.2f}",
                f"[{stock_style}]{p.stock}[/{stock_style}]",
            )
        console.print(table)

    def _show_cart(self):
        section("YOUR CART")
        if self.cart.is_empty():
            console.print("  [dim]Cart is empty.[/dim]")
            return
        table = make_table(
            {"header": "Item",     "style": "white",  "min_width": 20},
            {"header": "Qty",      "justify": "right","style": "yellow"},
            {"header": "Price",    "justify": "right","style": "cyan"},
            {"header": "Subtotal", "justify": "right","style": "green"},
        )
        for item in self.cart.items:
            table.add_row(
                item.product.name,
                str(item.quantity),
                f"${item.product.price:.2f}",
                f"${item.subtotal:.2f}",
            )
        console.print(table)
        console.print(f"  [bold green]Total: ${self.cart.total:.2f}[/bold green]")

    def _add_to_cart(self):
        self._show_products()
        try:
            pid = int(input("\n  Enter product ID: "))
            qty = int(input("  Enter quantity  : "))
            product = self.inventory.find_by_id(pid)
            if not product:
                flash_message("  ✘  Product not found.", "red")
                return
            self.cart.add_item(product, qty)
            flash_message(f"  ✔  Added {qty}x '{product.name}' to cart.", "green")
        except ValueError as e:
            flash_message(f"  ✘  {e}", "red")

    def _remove_from_cart(self):
        self._show_cart()
        if self.cart.is_empty():
            return
        try:
            pid = int(input("\n  Enter product ID to remove: "))
            self.cart.remove_item(pid)
            flash_message("  ✔  Item removed.", "green")
        except ValueError:
            flash_message("  ✘  Invalid input.", "red")

    def _checkout(self):
        self._show_cart()
        if self.cart.is_empty():
            return
        confirm = input("\n  Confirm checkout? (y/n): ").strip().lower()
        if confirm != "y":
            flash_message("  Checkout cancelled.", "yellow")
            return
        try:
            progress_bar("Processing payment...", steps=25, delay=0.04)
            order = self.checkout_service.process(self.cart, self.inventory)
            flash_message("  ✔  Payment successful!", "green")
            spinner("Printing receipt...", duration=0.8)
            self.receipt_printer.print(order)
        except ValueError as e:
            flash_message(f"  ✘  Checkout failed: {e}", "red")

    # ── Manager-only actions ──────────────────────────────────────────────────

    def _add_new_product(self):
        section("ADD PRODUCT")
        try:
            name  = input("  Product name : ").strip()
            price = float(input("  Price        : $"))
            stock = int(input("  Stock qty    : "))
            pid   = self.inventory.next_id()
            self.inventory.add_product(Product(pid, name, price, stock))
            spinner("Saving product...", duration=0.6)
            flash_message(f"  ✔  Product '{name}' added with ID {pid}.", "green")
        except ValueError as e:
            flash_message(f"  ✘  {e}", "red")

    def _show_transactions(self):
        section("TRANSACTION HISTORY")
        orders = load_orders()
        if not orders:
            console.print("  [dim]No transactions found.[/dim]")
            return

        table = make_table(
            {"header": "Order #",  "justify": "right", "style": "dim"},
            {"header": "Date",     "style": "white"},
            {"header": "Items",    "justify": "right", "style": "yellow"},
            {"header": "Total",    "justify": "right", "style": "green"},
        )
        for o in orders:
            table.add_row(
                str(o["order_id"]),
                o["timestamp"],
                str(len(o["items"])),
                f"${o['total']:.2f}",
            )
        console.print(table)
        console.print(f"  [dim]{len(orders)} transaction(s) on record.[/dim]")

        detail = input("\n  Enter Order # for detail (or Enter to go back): ").strip()
        if not detail:
            return
        matched = next((o for o in orders if str(o["order_id"]) == detail), None)
        if not matched:
            flash_message("  ✘  Order not found.", "red")
            return

        spinner("Loading order...", duration=0.5)
        section(f"ORDER #{matched['order_id']}")

        detail_table = make_table(
            {"header": "Item",     "style": "white", "min_width": 20},
            {"header": "Qty",      "justify": "right", "style": "yellow"},
            {"header": "Price",    "justify": "right", "style": "cyan"},
            {"header": "Subtotal", "justify": "right", "style": "green"},
        )
        for item in matched["items"]:
            detail_table.add_row(
                item["name"],
                str(item["quantity"]),
                f"${item['price']:.2f}",
                f"${item['subtotal']:.2f}",
            )
        console.print(detail_table)
        console.print(f"  [dim]Subtotal:[/dim] ${matched['subtotal']:.2f}")
        console.print(f"  [dim]Tax:     [/dim] ${matched['tax']:.2f}")
        console.print(f"  [bold green]Total:    ${matched['total']:.2f}[/bold green]")

    def _manage_users(self):
        section("MANAGE USERS")
        table = make_table(
            {"header": "Username", "style": "white", "min_width": 15},
            {"header": "Role",     "style": "cyan"},
        )
        for u in self.auth_service.get_all():
            role_style = "yellow" if u.role == "manager" else "cyan"
            table.add_row(u.username, f"[{role_style}]{u.role}[/{role_style}]")
        console.print(table)

        console.print("\n  [bold cyan]a.[/bold cyan]  Add new user")
        console.print("  [bold cyan]b.[/bold cyan]  Back")
        choice = input("  Select: ").strip().lower()
        if choice != "a":
            return
        try:
            username = input("  Username : ").strip()
            password = input("  Password : ").strip()
            console.print("  [dim]Roles: cashier / manager[/dim]")
            role = input("  Role     : ").strip().lower()
            self.auth_service.add_user(username, password, role)
            spinner("Saving user...", duration=0.6)
            flash_message(f"  ✔  User '{username}' added as {role}.", "green")
        except ValueError as e:
            flash_message(f"  ✘  {e}", "red")

    # ── Role loops ────────────────────────────────────────────────────────────

    def _run_cashier(self):
        while True:
            self._show_cashier_menu()
            match input("  Select option: ").strip():
                case "1": self._show_products()
                case "2": self._add_to_cart()
                case "3": self._show_cart()
                case "4": self._remove_from_cart()
                case "5": self._checkout()
                case "0": self._logout(); break
                case _:   flash_message("  ✘  Invalid option.", "red")
            if self.current_user:
                input("\n  Press Enter to continue...")

    def _run_manager(self):
        while True:
            self._show_manager_menu()
            match input("  Select option: ").strip():
                case "1": self._show_products()
                case "2": self._add_to_cart()
                case "3": self._show_cart()
                case "4": self._remove_from_cart()
                case "5": self._checkout()
                case "6": self._add_new_product()
                case "7": self._show_transactions()
                case "8": self._manage_users()
                case "0": self._logout(); break
                case _:   flash_message("  ✘  Invalid option.", "red")
            if self.current_user:
                input("\n  Press Enter to continue...")

    # ── Entry point ───────────────────────────────────────────────────────────

    def run(self):
        while True:
            if not self._login():
                break
            if self.current_user.is_manager():
                self._run_manager()
            else:
                self._run_cashier()

            again = input("\n  Switch user? (y/n): ").strip().lower()
            if again != "y":
                clear()
                console.print("\n  [bold cyan]System closed. See you next time![/bold cyan]\n")
                break


if __name__ == "__main__":
    POSApp().run()
