"""Search bar widget."""

from textual.widgets import Input, Static
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.message import Message


class SearchBar(Horizontal):
    """Search bar with input and filter buttons."""

    search_query: reactive[str] = reactive("")

    def compose(self):
        """Compose search bar layout."""
        yield Static("Search: ", classes="search-label")
        yield Input(placeholder="Type to filter projects...", id="search-input")
        yield Static("  Filters: [Status] [Priority] [Tag]", classes="filter-hint")

    def on_input_changed(self, event: Input.Changed):
        """Handle search input changes."""
        if event.input.id == "search-input":
            self.search_query = event.value
            # Post message to parent screen
            self.post_message(self.SearchChanged(event.value))

    class SearchChanged(Message):
        """Message sent when search query changes."""

        def __init__(self, query: str):
            super().__init__()
            self.query = query
