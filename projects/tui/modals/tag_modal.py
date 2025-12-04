"""Tag management modal for adding/removing project tags."""

from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Input, Button
from textual.binding import Binding

from .base_modal import BaseModal
from ...models import Project
from ... import database as db


class TagModal(BaseModal):
    """Modal for managing project tags."""

    BINDINGS = [
        Binding("escape", "dismiss", "Cancel"),
        Binding("ctrl+s", "save", "Save"),
        Binding("d", "delete_focused_tag", "Delete Tag"),
    ]

    def __init__(self, project: Project):
        super().__init__(title=f"Manage Tags - {project.name}", width=60, height=25)
        self.project = project
        self.current_tags = list(project.tags) if project.tags else []
        self.tags_to_add = []
        self.tags_to_remove = []

    def compose_body(self):
        """Compose the modal body with tag list and input."""
        yield Static("Current Tags:", classes="section-header")
        yield Static("Press Tab to navigate, 'd' to delete focused tag", classes="hint-text")

        # Container for tag chips
        with Container(id="tags-container"):
            if self.current_tags:
                for tag in self.current_tags:
                    yield from self._create_tag_chip_compose(tag)
            else:
                yield Static("No tags yet", id="no-tags", classes="dim")

        yield Static("\nAdd New Tag:", classes="section-header")
        yield Input(placeholder="Enter tag name and press Add Tag...", id="tag-input")

    def compose_buttons(self):
        """Compose modal buttons."""
        with Horizontal(id="modal-buttons"):
            yield Button("Add Tag", variant="primary", id="add-btn")
            yield Button("Save", variant="success", id="save-btn")
            yield Button("Cancel", variant="default", id="cancel-btn")

    def _create_tag_chip(self, tag: str) -> Horizontal:
        """Create a tag chip with remove button (for dynamic mounting)."""
        container = Horizontal(classes="tag-chip")
        container.compose_add_child(Static(f"🏷️  {tag}", classes="tag-text"))
        container.compose_add_child(Button("✖", variant="error", classes="remove-tag-btn", name=tag))
        return container

    def _create_tag_chip_compose(self, tag: str):
        """Create a tag chip with remove button (for compose method)."""
        with Horizontal(classes="tag-chip"):
            yield Static(f"🏷️  {tag}", classes="tag-text")
            yield Button("✖", variant="error", classes="remove-tag-btn", name=tag)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "add-btn":
            self._add_tag()
        elif event.button.id == "save-btn":
            self._save_tags()
        elif event.button.id == "cancel-btn":
            self.dismiss(False)
        elif event.button.classes and "remove-tag-btn" in event.button.classes:
            self._remove_tag(event.button.name)

    def _add_tag(self):
        """Add a new tag to the list."""
        tag_input = self.query_one("#tag-input", Input)
        new_tag = tag_input.value.strip()

        if not new_tag:
            self.notify("Tag name cannot be empty", severity="warning")
            return

        if new_tag in self.current_tags:
            self.notify(f"Tag '{new_tag}' already exists", severity="warning")
            return

        # Add to current tags and track for DB
        self.current_tags.append(new_tag)
        self.tags_to_add.append(new_tag)

        # Clear input
        tag_input.value = ""

        # Refresh tags display
        self._refresh_tags_display()
        self.notify(f"Added tag: {new_tag}", severity="information")

    def _remove_tag(self, tag: str):
        """Remove a tag from the list."""
        if tag in self.current_tags:
            self.current_tags.remove(tag)
            self.tags_to_remove.append(tag)

            # If it was in tags_to_add, just remove it from there
            if tag in self.tags_to_add:
                self.tags_to_add.remove(tag)

            self._refresh_tags_display()
            self.notify(f"Removed tag: {tag}", severity="information")

    def _refresh_tags_display(self):
        """Refresh the tags container display."""
        container = self.query_one("#tags-container")

        # Remove all children
        container.remove_children()

        # Re-add tags or "no tags" message
        if self.current_tags:
            for tag in self.current_tags:
                container.mount(self._create_tag_chip(tag))
        else:
            container.mount(Static("No tags yet", id="no-tags", classes="dim"))

    def _save_tags(self):
        """Save tag changes to database."""
        # Add new tags
        if self.tags_to_add:
            db.add_tags(self.project.name, self.tags_to_add)

        # Remove tags
        if self.tags_to_remove:
            for tag in self.tags_to_remove:
                db.remove_tags(self.project.name, [tag])

        # Update project object
        self.project.tags = self.current_tags

        self.dismiss(True)

    def action_save(self):
        """Handle Ctrl+S keybinding."""
        self._save_tags()

    def action_delete_focused_tag(self):
        """Delete the currently focused tag using 'd' key."""
        # Try to find focused button
        try:
            focused = self.app.focused
            if focused and isinstance(focused, Button):
                # Check if it's a remove tag button
                if focused.classes and "remove-tag-btn" in focused.classes:
                    tag_name = focused.name
                    if tag_name:
                        self._remove_tag(tag_name)
                        return

            # If no button focused, show message
            self.notify("Navigate to a tag and press 'd' to delete it", severity="information")
        except Exception:
            self.notify("Navigate to a tag and press 'd' to delete it", severity="information")
