"""Search bar widget."""

from textual.widgets import Input, Static
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.message import Message
from textual.events import Key


class SearchBar(Horizontal):
    """Search bar with input and filter buttons."""

    search_query: reactive[str] = reactive("")

    def compose(self):
        """Compose search bar layout."""
        yield Input(
            placeholder="🔍 Search projects... (Enter to apply, ESC to clear)",
            id="search-input"
        )

    def on_input_changed(self, event: Input.Changed):
        """Handle search input changes."""
        if event.input.id == "search-input":
            self.search_query = event.value
            # Post message to parent screen
            self.post_message(self.SearchChanged(event.value))

    def on_key(self, event: Key) -> None:
        """Handle key events in search bar."""
        if event.key == "enter":
            # Focus back to the table when Enter is pressed
            self.post_message(self.SearchSubmitted())

    class SearchChanged(Message):
        """Message sent when search query changes."""

        def __init__(self, query: str):
            super().__init__()
            self.query = query

    class SearchSubmitted(Message):
        """Message sent when Enter is pressed in search."""
        pass
