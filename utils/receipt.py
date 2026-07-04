import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from fpdf import FPDF

console = Console()

RECEIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "receipts")


class ReceiptPrinter:

    def print(self, order):
        self._print_console(order)
        path = self._save_pdf(order)
        console.print(f"\n  [dim]PDF saved → {path}[/dim]")

    # ── Console receipt (Rich) ────────────────────────────────────────────────

    def _print_console(self, order):
        table = Table(
            box=box.SIMPLE_HEAVY,
            border_style="bright_black",
            header_style="bold cyan",
            show_lines=False,
            min_width=46,
        )
        table.add_column("Item",    style="white",        min_width=20)
        table.add_column("Qty",     justify="right",      style="yellow")
        table.add_column("Price",   justify="right",      style="cyan")
        table.add_column("Subtotal",justify="right",      style="green")

        for item in order.items:
            table.add_row(
                item.product.name,
                str(item.quantity),
                f"${item.product.price:.2f}",
                f"${item.subtotal:.2f}",
            )

        summary = (
            f"[dim]Subtotal:[/dim]  ${order.subtotal:.2f}\n"
            f"[dim]Tax (8%):[/dim]  ${order.tax:.2f}\n"
            f"[bold green]TOTAL:    ${order.total:.2f}[/bold green]"
        )

        header = Text.assemble(
            ("🧾  MINI SHOP RECEIPT\n", "bold white"),
            (f"Order #: {order.order_id}   ", "dim"),
            (order.timestamp.strftime("%Y-%m-%d %H:%M:%S"), "dim"),
        )

        console.print()
        console.print(Panel(header, border_style="cyan", padding=(0, 2)))
        console.print(table)
        console.print(Panel(summary, border_style="dim", padding=(0, 2)))
        console.print("  [bold cyan]Thank you for shopping! 🙏[/bold cyan]\n")

    # ── PDF receipt (fpdf2) ───────────────────────────────────────────────────

    def _save_pdf(self, order):
        os.makedirs(RECEIPTS_DIR, exist_ok=True)
        path = os.path.join(RECEIPTS_DIR, f"receipt_{order.order_id}.pdf")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_margins(20, 20, 20)

        # Header
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "MINI SHOP RECEIPT", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Order #: {order.order_id}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Date   : {order.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        # Table header
        pdf.set_fill_color(30, 30, 30)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 10)
        col_w = [80, 20, 35, 35]
        headers = ["Item", "Qty", "Price", "Subtotal"]
        for i, h in enumerate(headers):
            align = "L" if i == 0 else "R"
            pdf.cell(col_w[i], 8, h, border=1, align=align, fill=True)
        pdf.ln()

        # Table rows
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 10)
        fill = False
        for item in order.items:
            pdf.set_fill_color(245, 245, 245) if fill else pdf.set_fill_color(255, 255, 255)
            pdf.cell(col_w[0], 7, item.product.name,           border=1, align="L", fill=True)
            pdf.cell(col_w[1], 7, str(item.quantity),           border=1, align="R", fill=True)
            pdf.cell(col_w[2], 7, f"${item.product.price:.2f}", border=1, align="R", fill=True)
            pdf.cell(col_w[3], 7, f"${item.subtotal:.2f}",      border=1, align="R", fill=True)
            pdf.ln()
            fill = not fill

        # Totals
        pdf.ln(3)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(135, 7, "Subtotal", align="R")
        pdf.cell(35,  7, f"${order.subtotal:.2f}", align="R", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(135, 7, "Tax (8%)", align="R")
        pdf.cell(35,  7, f"${order.tax:.2f}", align="R", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(135, 8, "TOTAL", align="R")
        pdf.cell(35,  8, f"${order.total:.2f}", align="R", new_x="LMARGIN", new_y="NEXT")

        # Footer
        pdf.ln(6)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 6, "Thank you for shopping!", align="C")

        pdf.output(path)
        return path
