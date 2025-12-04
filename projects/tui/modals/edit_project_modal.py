"""Edit project modal for modifying project details."""

from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Input, Button, Select
from textual.binding import Binding

from .base_modal import BaseModal
from ...models import Project
from ... import database as db


class EditProjectModal(BaseModal):
    """Modal for editing project details."""

    BINDINGS = [
        Binding("escape", "dismiss", "Cancel"),
        Binding("ctrl+s", "save", "Save"),
    ]

    def __init__(self, project: Project):
        super().__init__(title=f"Edit Project - {project.name}", width=70, height=25)
        self.project = project

    def compose_body(self):
        """Compose the modal body with input fields."""
        yield Static("Project Name:", classes="field-label")
        yield Input(value=self.project.name, placeholder="Enter project name...", id="name-input")

        yield Static("\nDescription:", classes="field-label")
        yield Input(
            value=self.project.description or "",
            placeholder="Enter description...",
            id="description-input"
        )

        yield Static("\nPath:", classes="field-label")
        yield Input(
            value=self.project.path or "",
            placeholder="e.g., ~/projects/myapp",
            id="path-input"
        )

        yield Static("\nPriority:", classes="field-label")
        yield Select(
            [
                ("High", "high"),
                ("Medium", "medium"),
                ("Low", "low"),
            ],
            value=self.project.priority,
            id="priority-select"
        )

    def compose_buttons(self):
        """Compose modal buttons."""
        with Horizontal(id="modal-buttons"):
            yield Button("Save Changes", variant="success", id="save-btn")
            yield Button("Cancel", variant="default", id="cancel-btn")

    async def on_mount(self):
        """Focus the name input when modal opens."""
        name_input = self.query_one("#name-input", Input)
        name_input.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save-btn":
            self._save_changes()
        elif event.button.id == "cancel-btn":
            self.dismiss(False)

    def _save_changes(self):
        """Validate and save the changes."""
        # Get new values
        new_name = self.query_one("#name-input", Input).value.strip()
        new_description = self.query_one("#description-input", Input).value.strip() or None
        new_path = self.query_one("#path-input", Input).value.strip() or None
        new_priority = self.query_one("#priority-select", Select).value

        # Validate name
        if not new_name:
            self.notify("Project name cannot be empty", severity="error")
            return

        # Track if any changes were made
        updated = False
        old_name = self.project.name

        # Update name if changed
        if new_name != old_name:
            # Check if new name already exists
            if db.get_project(new_name):
                self.notify(f"Project '{new_name}' already exists", severity="error")
                return

            if db.update_project_field(old_name, "name", new_name):
                self.project.name = new_name
                updated = True
            else:
                self.notify("Failed to update name", severity="error")
                return

        # Update description if changed
        if new_description != self.project.description:
            if db.update_project_field(self.project.name, "description", new_description):
                self.project.description = new_description
                updated = True

        # Update path if changed
        if new_path != self.project.path:
            if db.update_project_field(self.project.name, "path", new_path):
                self.project.path = new_path
                updated = True

        # Update priority if changed
        if new_priority != self.project.priority:
            if db.update_project_field(self.project.name, "priority", new_priority):
                self.project.priority = new_priority
                updated = True

        if updated:
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_save(self):
        """Handle Ctrl+S keybinding."""
        self._save_changes()
