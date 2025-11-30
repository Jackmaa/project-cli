"""Quick actions widget."""

from textual.widgets import Static
from textual.containers import Horizontal


class QuickActions(Horizontal):
    """Quick actions panel with action hints."""

    def compose(self):
        """Compose quick actions layout."""
        yield Static(
            "[1/2/3] Priority  [A/P/C/X] Status  [O/Enter] Open  [R] Refresh  [/] Search  [Q] Quit",
            classes="quick-actions-text"
        )
