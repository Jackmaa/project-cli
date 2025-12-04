"""Help modal showing all keybindings."""

from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.widgets import Static, Button
from textual.binding import Binding

from .base_modal import BaseModal


class HelpModal(BaseModal):
    """Modal displaying all available keybindings."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
    ]

    def __init__(self):
        super().__init__(title="Keyboard Shortcuts", width=80, height=35)

    def compose_body(self):
        """Compose the help content with keybindings."""
        with VerticalScroll():
            # Status Changes
            yield Static("Status Changes", classes="help-section-header")
            yield from self._create_keybind_row("a", "Set project to Active")
            yield from self._create_keybind_row("p", "Set project to Paused")
            yield from self._create_keybind_row("c", "Set project to Completed")
            yield from self._create_keybind_row("x", "Set project to Abandoned")

            # Priority Changes
            yield Static("\nPriority Changes", classes="help-section-header")
            yield from self._create_keybind_row("1", "Set priority to High")
            yield from self._create_keybind_row("2", "Set priority to Medium")
            yield from self._create_keybind_row("3", "Set priority to Low")

            # Project Management
            yield Static("\nProject Management", classes="help-section-header")
            yield from self._create_keybind_row("n", "Add new project")
            yield from self._create_keybind_row("e", "Edit selected project")
            yield from self._create_keybind_row("d", "Delete selected project")
            yield from self._create_keybind_row("s", "Scan directory for projects")
            yield from self._create_keybind_row("t", "Manage tags")
            yield from self._create_keybind_row("i", "Toggle info panel")

            # Actions
            yield Static("\nActions", classes="help-section-header")
            yield from self._create_keybind_row("o", "Open project in IDE")
            yield from self._create_keybind_row("r", "Refresh git status (local)")

            # Navigation
            yield Static("\nNavigation", classes="help-section-header")
            yield from self._create_keybind_row("/", "Focus search bar")
            yield from self._create_keybind_row("Escape", "Clear search / Close modals")
            yield from self._create_keybind_row("Tab", "Navigate between elements")
            yield from self._create_keybind_row("↑ ↓", "Navigate table rows")

            # Other
            yield Static("\nOther", classes="help-section-header")
            yield from self._create_keybind_row("?", "Show this help menu")
            yield from self._create_keybind_row("q", "Quit application")

    def _create_keybind_row(self, key: str, description: str):
        """Create a row showing a keybinding."""
        with Horizontal(classes="help-row"):
            yield Static(f"[bold cyan]{key}[/]", classes="help-key")
            yield Static(description, classes="help-desc")

    def compose_buttons(self):
        """Compose modal buttons."""
        with Horizontal(id="modal-buttons"):
            yield Button("Close", variant="primary", id="close-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "close-btn":
            self.dismiss(None)
