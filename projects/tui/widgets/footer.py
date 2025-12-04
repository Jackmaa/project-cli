"""Footer widget displaying keyboard shortcuts."""

from textual.widgets import Static
from rich.table import Table
from rich.text import Text


class Footer(Static):
    """Footer widget showing keyboard shortcuts like vim status line."""

    DEFAULT_CSS = """
    Footer {
        height: 2;
        background: $panel;
        color: $text;
        dock: bottom;
    }
    """

    def render(self):
        """Render footer with essential shortcuts and help prompt."""
        table = Table.grid(expand=True, padding=0)
        table.add_column(justify="left")
        table.add_column(justify="center")
        table.add_column(justify="right")

        # Essential shortcuts only
        left = Text()
        left.append("n", style="bold green")
        left.append(":new  ")
        left.append("e", style="bold blue")
        left.append(":edit  ")
        left.append("d", style="bold red")
        left.append(":delete  ")
        left.append("o", style="bold green")
        left.append(":open")

        center = Text()
        center.append("Press ", style="dim")
        center.append("?", style="bold yellow")
        center.append(" for help", style="dim")

        right = Text()
        right.append("/", style="bold magenta")
        right.append(":search  ")
        right.append("q", style="bold red")
        right.append(":quit")

        table.add_row(left, center, right)

        return table
