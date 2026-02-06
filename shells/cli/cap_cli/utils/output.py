"""Output formatting utilities using Rich."""

from rich.console import Console


# Global console instance
console = Console()


def print_success(message: str):
    """Print success message in green."""
    console.print(f"[OK] {message}", style="bold green")


def print_error(message: str):
    """Print error message in red."""
    console.print(f"[ERROR] {message}", style="bold red")


def print_warning(message: str):
    """Print warning message in yellow."""
    console.print(f"[WARNING] {message}", style="bold yellow")


def print_info(message: str):
    """Print info message in blue."""
    console.print(f"[INFO] {message}", style="bold blue")
