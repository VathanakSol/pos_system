import time
import os

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich import box

console = Console()


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def typewrite(text, delay=0.03):
    """Animated typewriter using rich markup."""
    for ch in text:
        console.print(ch, end="", highlight=False)
        time.sleep(delay)
    console.print()


def spinner(message, duration=1.0):
    from rich.spinner import Spinner
    from rich.live import Live
    with Live(Spinner("dots", text=f" {message}"), console=console, refresh_per_second=12):
        time.sleep(duration)


def progress_bar(message, steps=25, delay=0.04):
    with Progress(
        TextColumn("  [bold cyan]{task.description}"),
        BarColumn(bar_width=30, complete_style="green", finished_style="bright_green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task(message, total=steps)
        for _ in range(steps):
            time.sleep(delay)
            progress.advance(task)


def flash_message(message, color="green"):
    style_map = {"green": "bold green", "red": "bold red", "yellow": "bold yellow"}
    console.print(f"  {message}", style=style_map.get(color, ""))


def banner():
    clear()
    title = Text("🛒  MINI POS SYSTEM  🛒", justify="center")
    title.stylize("bold cyan")
    console.print(Panel(title, border_style="cyan", padding=(1, 4)))
    console.print()


def section(title):
    console.rule(f"[bold yellow]{title}[/bold yellow]")


def divider():
    console.rule(style="dim")


def make_table(*columns, title=None, box_style=box.SIMPLE_HEAVY):
    """Helper to create a styled Rich table."""
    t = Table(title=title, box=box_style, border_style="bright_black",
              header_style="bold cyan", show_lines=False)
    for col in columns:
        if isinstance(col, dict):
            t.add_column(**col)
        else:
            t.add_column(col)
    return t
