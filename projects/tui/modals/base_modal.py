"""Base modal class for TUI overlays."""

from textual.screen import ModalScreen
from textual.containers import Container, Vertical
from textual.widgets import Static, Button
from textual.binding import Binding


class BaseModal(ModalScreen):
    """Base class for modal dialogs."""

    BINDINGS = [
        Binding("escape", "dismiss", "Cancel"),
    ]

    def __init__(self, title: str = "Modal", width: int = 60, height: int = 20):
        super().__init__()
        self.modal_title = title
        self.modal_width = width
        self.modal_height = height

    def compose(self):
        """Compose modal layout."""
        with Container(id="modal-container"):
            with Vertical(id="modal-content"):
                yield Static(self.modal_title, id="modal-title")
                yield from self.compose_body()
                yield from self.compose_buttons()

    def compose_body(self):
        """Override in subclasses to add modal content."""
        raise NotImplementedError

    def compose_buttons(self):
        """Override in subclasses to add buttons."""
        yield Button("Cancel", variant="default", id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed):
        """Handle button clicks."""
        if event.button.id == "cancel-btn":
            self.dismiss(None)

    def action_dismiss(self):
        """Dismiss modal."""
        self.dismiss(None)
