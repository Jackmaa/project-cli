"""Confirmation modal for destructive actions."""

from textual.widgets import Static, Button
from textual.containers import Horizontal
from .base_modal import BaseModal


class ConfirmationModal(BaseModal):
    """Modal for confirming actions."""

    def __init__(
        self,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        confirm_variant: str = "error"
    ):
        super().__init__(title=title, width=60, height=15)
        self.message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.confirm_variant = confirm_variant

    def compose_body(self):
        """Compose confirmation message."""
        yield Static(self.message, id="confirmation-message")

    def compose_buttons(self):
        """Compose action buttons."""
        with Horizontal(id="modal-buttons"):
            yield Button(self.cancel_text, variant="default", id="cancel-btn")
            yield Button(
                self.confirm_text,
                variant=self.confirm_variant,
                id="confirm-btn"
            )

    def on_button_pressed(self, event: Button.Pressed):
        """Handle button clicks."""
        if event.button.id == "confirm-btn":
            self.dismiss(True)
        else:
            self.dismiss(False)
