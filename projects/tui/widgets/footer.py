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
        """Render footer with two rows of keyboard shortcuts."""
        table = Table.grid(expand=True, padding=0)
        table.add_column(justify="left")
        table.add_column(justify="right")

        # Row 1 - Status and Priority shortcuts
        left1 = Text()
        left1.append("a", style="bold cyan")
        left1.append(":active ")
        left1.append("p", style="bold cyan")
        left1.append(":paused ")
        left1.append("c", style="bold cyan")
        left1.append(":completed ")
        left1.append("x", style="bold cyan")
        left1.append(":abandoned")

        right1 = Text()
        right1.append("1", style="bold yellow")
        right1.append(":high ")
        right1.append("2", style="bold yellow")
        right1.append(":med ")
        right1.append("3", style="bold yellow")
        right1.append(":low")

        table.add_row(left1, right1)

        # Row 2 - Action shortcuts
        left2 = Text()
        left2.append("o", style="bold green")
        left2.append("/")
        left2.append("↵", style="bold green")
        left2.append(":open ")
        left2.append("r", style="bold green")
        left2.append(":refresh ")
        left2.append("q", style="bold red")
        left2.append(":quit")

        right2 = Text()
        right2.append("/", style="bold magenta")
        right2.append(":search ")
        right2.append("f", style="bold magenta")
        right2.append(":filter")

        table.add_row(left2, right2)

        return table
