"""Add project modal for creating new projects."""

from pathlib import Path
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Input, Button, Select, Checkbox
from textual.binding import Binding
from textual.reactive import reactive
from textual.worker import Worker, WorkerState

from .base_modal import BaseModal
from ... import database as db
from ... import templates as tmpl
from ... import scaffold


class AddProjectModal(BaseModal):
    """Modal for adding a new project."""

    BINDINGS = [
        Binding("escape", "dismiss", "Cancel"),
        Binding("ctrl+s", "save", "Save"),
    ]

    def __init__(self):
        super().__init__(title="Add New Project", width=70, height=35)
        self.selected_template_id = "custom"
        self.scaffold_worker = None
        self.pending_project_data = None

    def compose_body(self):
        """Compose the modal body with input fields."""
        yield Static("Project Template:", classes="field-label")

        # Build template options organized by category
        template_options = []
        categories = tmpl.get_templates_by_category()

        for category, templates in categories.items():
            # Add category header (disabled option)
            template_options.append((f"─── {category} ───", f"__category_{category}"))
            # Add templates in this category
            for template_id, template_name in templates:
                template_options.append((f"  {template_name}", template_id))

        yield Select(
            options=template_options,
            value="custom",
            id="template-select",
            allow_blank=False
        )

        yield Static("\nProject Name:", classes="field-label")
        yield Input(placeholder="Enter project name...", id="name-input")

        yield Static("\nDescription (optional):", classes="field-label")
        yield Input(placeholder="Enter description...", id="description-input")

        yield Static("\nProject Location:", classes="field-label")
        yield Checkbox("Create project folder from template", value=False, id="scaffold-checkbox")
        yield Static("Base directory (where project folder will be created):", classes="hint-text")
        yield Input(placeholder="e.g., ~/projects", id="base-dir-input")
        yield Static("Or specify full project path:", classes="hint-text")
        yield Input(placeholder="e.g., ~/projects/myapp", id="path-input")

        yield Static("\nPriority:", classes="field-label")
        yield Select(
            [
                ("High", "high"),
                ("Medium", "medium"),
                ("Low", "low"),
            ],
            value="medium",
            id="priority-select"
        )

        yield Static("\nAdditional Tags (optional):", classes="field-label")
        yield Static("", id="template-info", classes="hint-text")
        yield Input(placeholder="e.g., personal, work", id="tags-input")

    def compose_buttons(self):
        """Compose modal buttons."""
        with Horizontal(id="modal-buttons"):
            yield Button("Add Project", variant="success", id="add-btn")
            yield Button("Cancel", variant="default", id="cancel-btn")

    async def on_mount(self):
        """Focus the template select when modal opens."""
        template_select = self.query_one("#template-select", Select)
        template_select.focus()
        # Update template info on mount
        self._update_template_info("custom")

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle template selection change."""
        if event.select.id == "template-select":
            self._update_template_info(event.value)

    def _update_template_info(self, template_id: str) -> None:
        """Update the template info display."""
        self.selected_template_id = template_id

        # Don't show info for category headers
        if template_id.startswith("__category_"):
            return

        template_info = self.query_one("#template-info", Static)

        if template_id == "custom" or not template_id:
            template_info.update("No template selected")
            return

        template = tmpl.get_template(template_id)
        if template:
            tags_str = ", ".join(template["tags"]) if template["tags"] else "none"
            language = template["language"] or "auto-detect"
            template_info.update(f"Language: {language} | Tags: {tags_str}")
        else:
            template_info.update("Template not found")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "add-btn":
            self._add_project()
        elif event.button.id == "cancel-btn":
            self.dismiss(None)

    def _detect_language(self, path: Path) -> str | None:
        """Detect the primary language in a project directory."""
        language_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".jsx": "JavaScript",
            ".tsx": "TypeScript",
            ".rs": "Rust",
            ".go": "Go",
            ".java": "Java",
            ".c": "C",
            ".cpp": "C++",
            ".cs": "C#",
            ".rb": "Ruby",
            ".php": "PHP",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".dart": "Dart",
            ".vue": "Vue",
            ".html": "HTML",
            ".css": "CSS",
            ".sh": "Shell",
        }

        extension_counts = {}

        try:
            for file in path.rglob("*"):
                if file.is_file():
                    ext = file.suffix.lower()
                    if ext in language_map:
                        extension_counts[ext] = extension_counts.get(ext, 0) + 1
        except PermissionError:
            pass

        if extension_counts:
            most_common_ext = max(extension_counts, key=extension_counts.get)
            return language_map[most_common_ext]

        return None

    def _add_project(self):
        """Validate and add the new project."""
        # Get values
        template_id = self.query_one("#template-select", Select).value
        name = self.query_one("#name-input", Input).value.strip()
        description = self.query_one("#description-input", Input).value.strip() or None
        should_scaffold = self.query_one("#scaffold-checkbox", Checkbox).value
        base_dir_str = self.query_one("#base-dir-input", Input).value.strip()
        path_str = self.query_one("#path-input", Input).value.strip()
        priority = self.query_one("#priority-select", Select).value
        additional_tags_str = self.query_one("#tags-input", Input).value.strip()

        # Validate name
        if not name:
            self.notify("Project name is required", severity="error")
            return

        # Skip category headers (they start with __category_)
        if template_id and template_id.startswith("__category_"):
            self.notify("Please select a template, not a category", severity="error")
            return

        # Check if project already exists
        if db.get_project(name):
            self.notify(f"Project '{name}' already exists", severity="error")
            return

        # Get template and apply it
        language = None
        tags = []

        if template_id and template_id != "custom":
            template = tmpl.get_template(template_id)
            if template:
                language = template["language"]
                tags = list(template["tags"])  # Copy template tags

        # Handle scaffolding if requested
        path = None
        if should_scaffold:
            if not base_dir_str:
                self.notify("Base directory is required when creating from template", severity="error")
                return

            if template_id == "custom" or not template_id:
                self.notify("Please select a template to scaffold from", severity="error")
                return

            base_dir = Path(base_dir_str).expanduser().resolve()

            # Scaffold the project
            # Note: This can take a while (30-60 seconds for some templates)
            # Disable buttons during scaffolding
            add_btn = self.query_one("#add-btn", Button)
            cancel_btn = self.query_one("#cancel-btn", Button)
            add_btn.disabled = True
            cancel_btn.disabled = True

            self.notify(f"Creating project (this may take up to a minute, please wait)...", severity="information")

            try:
                result, message = scaffold.scaffold_project(template_id, name, base_dir)

                # Re-enable buttons
                add_btn.disabled = False
                cancel_btn.disabled = False

                if result == "success":
                    path = str(base_dir / name)
                    self.notify(message, severity="information")
                elif result == "exists":
                    self.notify(message, severity="error")
                    return
                elif result == "unsupported":
                    self.notify(message, severity="warning")
                    # Continue without path
                else:  # error
                    self.notify(message, severity="error")
                    return
            except Exception as e:
                # Re-enable buttons on error
                add_btn.disabled = False
                cancel_btn.disabled = False
                self.notify(f"Scaffolding failed: {str(e)}", severity="error")
                return
        elif path_str:
            # Use provided path
            path_obj = Path(path_str).expanduser().resolve()
            if not path_obj.exists():
                self.notify(f"Path does not exist: {path_str}", severity="error")
                return
            path = str(path_obj)

            # Only auto-detect language if no template was selected or template is custom
            if not language or template_id == "custom":
                language = self._detect_language(path_obj)

        # Add additional tags from user input
        if additional_tags_str:
            additional_tags = [t.strip() for t in additional_tags_str.split(",") if t.strip()]
            # Merge with template tags, avoiding duplicates
            for tag in additional_tags:
                if tag not in tags:
                    tags.append(tag)

        # Add to database
        success = db.add_project(
            name=name,
            description=description,
            path=path,
            priority=priority,
            language=language,
            tags=tags,
        )

        if success:
            self.dismiss(True)
        else:
            self.notify(f"Failed to add project '{name}'", severity="error")

    def action_save(self):
        """Handle Ctrl+S keybinding."""
        self._add_project()
