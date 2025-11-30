"""Quick actions widget."""

from textual.widgets import Static
from textual.containers import Horizontal


class QuickActions(Horizontal):
    """Quick actions panel with action hints."""

    def compose(self):
        """Compose quick actions layout."""
        yield Static(
            "Quick Actions: [O]pen IDE  [I]nfo  [T]ree  [C]ommits  [G]itHub",
            classes="quick-actions-text"
        )
