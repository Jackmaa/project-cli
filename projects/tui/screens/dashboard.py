"""Main dashboard screen."""

from textual.screen import Screen
from textual.reactive import reactive
from textual.binding import Binding
from textual.events import Key
import subprocess
from pathlib import Path
import time
import os

from ...models import Project
from ... import database as db
from ... import config
from ..widgets import (
    ProjectsTable,
    StatsPanel,
    GitOverview,
    SearchBar,
    Footer,
)
from ..panels import DetailPanel
from ..modals import TagModal, AddProjectModal, EditProjectModal, ScanModal, ConfirmationModal, HelpModal


class DashboardScreen(Screen):
    """Main dashboard screen with all panels and state management."""

    BINDINGS = [
        # Status changes
        Binding("a", "set_status('active')", "Active"),
        Binding("p", "set_status('paused')", "Pause"),
        Binding("c", "set_status('completed')", "Complete"),
        Binding("x", "set_status('abandoned')", "Abandon"),
        # Priority changes
        Binding("1", "set_priority('high')", "High"),
        Binding("2", "set_priority('medium')", "Medium"),
        Binding("3", "set_priority('low')", "Low"),
        # Actions
        Binding("i", "toggle_info", "Info"),
        Binding("t", "manage_tags", "Tags"),
        Binding("o", "open_ide", "Open"),
        Binding("r", "refresh_git", "Refresh"),
        # Project management
        Binding("n", "add_project", "New"),
        Binding("e", "edit_project", "Edit"),
        Binding("d", "delete_project", "Delete"),
        Binding("s", "scan_directory", "Scan"),
        # Navigation
        Binding("/", "focus_search", "Search"),
        Binding("escape", "clear_search", "Clear Search"),
        Binding("?", "show_help", "Help"),
        Binding("q", "quit", "Quit"),
    ]

    # State
    all_projects: list[Project] = []
    projects: reactive[list[Project]] = reactive([])
    search_query: reactive[str] = reactive("")
    status_filter: reactive[str | None] = reactive(None)
    tag_filter: reactive[str | None] = reactive(None)
    priority_filter: reactive[str | None] = reactive(None)

    # Info panel state
    info_panel_visible: reactive[bool] = reactive(False)
    selected_project: reactive[Project | None] = reactive(None)

    # Debouncing for actions (prevent rapid-fire events)
    _last_action_time: float = 0
    _min_action_interval: float = 0.3  # 300ms between actions

    # Track last key for sequence detection
    _last_key: str = ""
    _last_key_time: float = 0

    # Debug mode - set DEBUG_TUI=1 environment variable to enable
    _debug_enabled: bool = os.getenv("DEBUG_TUI") == "1"
    _debug_log_path: Path = Path.home() / ".config" / "project-cli" / "tui_debug.log"

    def _debug_log(self, message: str):
        """Log debug message to file if debug mode is enabled."""
        if not self._debug_enabled:
            return

        try:
            with open(self._debug_log_path, "a") as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {message}\n")
        except Exception:
            pass  # Ignore logging errors

    def compose(self):
        """Compose dashboard layout."""
        # Note: DetailPanel is mounted dynamically in watch_info_panel_visible()
        yield SearchBar()
        yield StatsPanel()
        yield GitOverview()
        yield ProjectsTable()
        yield Footer()

    async def on_mount(self):
        """Load data when screen mounts."""
        self._debug_log("=== Dashboard mounted ===")

        # Clear old debug log
        if self._debug_enabled:
            try:
                self._debug_log_path.parent.mkdir(parents=True, exist_ok=True)
                if self._debug_log_path.exists():
                    self._debug_log_path.unlink()
            except Exception:
                pass

        # Load all projects from database
        self.all_projects = db.get_all_projects()
        self.projects = self.all_projects.copy()

        # Populate widgets
        table = self.query_one(ProjectsTable)
        table.populate(self.projects)
        table.focus()

        # Update panels
        self.query_one(StatsPanel).projects = self.projects
        self.query_one(GitOverview).projects = self.projects

    def watch_projects(self, projects: list[Project]):
        """React to projects list changes."""
        self.query_one(ProjectsTable).populate(projects)
        self.query_one(StatsPanel).projects = projects
        self.query_one(GitOverview).projects = projects

    def on_search_bar_search_changed(self, message: SearchBar.SearchChanged):
        """Handle search query changes."""
        self.search_query = message.query
        self.apply_filters()

    def on_search_bar_search_submitted(self, message: SearchBar.SearchSubmitted):
        """Handle search submission (Enter pressed)."""
        # Return focus to the table
        table = self.query_one(ProjectsTable)
        table.focus()

    def apply_filters(self):
        """Apply all active filters to projects list."""
        filtered = self.all_projects

        # Apply search query (fuzzy match on name)
        if self.search_query:
            filtered = [
                p for p in filtered
                if self.fuzzy_match(self.search_query, p.name)
            ]

        # Apply status filter
        if self.status_filter:
            filtered = [p for p in filtered if p.status == self.status_filter]

        # Apply tag filter
        if self.tag_filter:
            filtered = [p for p in filtered if self.tag_filter in p.tags]

        # Apply priority filter
        if self.priority_filter:
            filtered = [p for p in filtered if p.priority == self.priority_filter]

        # Update reactive property
        self.projects = filtered

    @staticmethod
    def fuzzy_match(query: str, text: str) -> bool:
        """Simple fuzzy matching - all query chars must appear in order."""
        query = query.lower()
        text = text.lower()
        query_idx = 0
        for char in text:
            if query_idx < len(query) and char == query[query_idx]:
                query_idx += 1
        return query_idx == len(query)

    def _check_debounce(self) -> bool:
        """Check if enough time has passed since last action."""
        current_time = time.time()
        if current_time - self._last_action_time < self._min_action_interval:
            return False
        self._last_action_time = current_time
        return True

    def action_set_status(self, status: str):
        """Handle status change action."""
        self._debug_log(f"ACTION: set_status('{status}')")

        if not self._check_debounce():
            self._debug_log("  -> BLOCKED by debounce")
            return

        selected = self.query_one(ProjectsTable).get_selected_project()
        if not selected:
            self._debug_log("  -> No project selected")
            self.notify("No project selected", severity="warning")
            return

        self._debug_log(f"  -> Setting {selected.name} to {status}")
        if db.update_project_status(selected.name, status):
            selected.status = status
            self.apply_filters()
            self.notify(f"Set {selected.name} to {status}", severity="information")
        else:
            self.notify("Failed to update status", severity="error")

    def action_set_priority(self, priority: str):
        """Handle priority change action."""
        self._debug_log(f"ACTION: set_priority('{priority}')")

        if not self._check_debounce():
            self._debug_log("  -> BLOCKED by debounce")
            return

        selected = self.query_one(ProjectsTable).get_selected_project()
        if not selected:
            self._debug_log("  -> No project selected")
            self.notify("No project selected", severity="warning")
            return

        self._debug_log(f"  -> Setting {selected.name} priority to {priority}")
        if db.update_project_field(selected.name, "priority", priority):
            selected.priority = priority
            self.apply_filters()
            self.notify(f"Set {selected.name} priority to {priority}", severity="information")
        else:
            self.notify("Failed to update priority", severity="error")

    def action_open_ide(self):
        """Handle open IDE action."""
        selected = self.query_one(ProjectsTable).get_selected_project()
        if not selected:
            self.notify("No project selected", severity="warning")
            return

        if not selected.path:
            self.notify(f"{selected.name} has no path configured", severity="warning")
            return

        path = Path(selected.path)
        if not path.exists():
            self.notify(f"Path does not exist: {selected.path}", severity="error")
            return

        # Get IDE from config
        ide = config.get_ide()
        if not ide:
            self.notify("No IDE configured. Run 'projects config --set-ide'", severity="warning")
            return

        # Open IDE in background
        try:
            subprocess.Popen([ide, str(path)])
            self.notify(f"Opening {selected.name} in {ide}", severity="information")
        except Exception as e:
            self.notify(f"Failed to open IDE: {e}", severity="error")

    async def action_refresh_git(self):
        """Handle git refresh action (local only, no remote fetch)."""
        self.notify("Refreshing git status (local only)...", timeout=2)

        # Update git status for all projects (without remote fetch to avoid SSH prompts)
        for project in self.all_projects:
            if project.path:
                try:
                    db.update_git_status_for_project(project, fetch=False)
                except Exception:
                    pass  # Continue with other projects

        # Reload projects from database
        self.all_projects = db.get_all_projects()
        self.apply_filters()

        self.notify("Git status refreshed (use CLI 'projects refresh --fetch' for remote)", severity="information")

    def action_focus_search(self):
        """Focus the search input."""
        search_input = self.query_one("#search-input", Input)
        search_input.focus()

    def action_clear_search(self):
        """Clear search and return focus to table."""
        # Clear the search input
        search_input = self.query_one("#search-input", Input)
        search_input.value = ""

        # Return focus to table
        table = self.query_one(ProjectsTable)
        table.focus()

    def action_quit(self):
        """Quit the application."""
        self.app.exit()

    def action_show_help(self):
        """Show help modal with keybindings."""
        self.app.push_screen(HelpModal())

    def action_toggle_info(self):
        """Toggle info panel visibility."""
        old_state = self.info_panel_visible

        # Set selected project BEFORE toggling visibility (so watcher can use it)
        if not old_state:  # If we're about to show the panel
            table = self.query_one(ProjectsTable)
            self.selected_project = table.get_selected_project()

        # Now toggle visibility (this triggers the watcher)
        self.info_panel_visible = not self.info_panel_visible

    def action_manage_tags(self):
        """Manage tags for the selected project."""
        selected = self.query_one(ProjectsTable).get_selected_project()
        if not selected:
            self.notify("No project selected", severity="warning")
            return

        # Store selected project name for the callback
        self._editing_tags_for = selected.name

        self.app.push_screen(TagModal(selected), callback=self._on_tags_updated)

    def _on_tags_updated(self, result):
        """Handle tag modal dismissal."""
        if result:
            # Reload projects from database to get updated tags
            self.all_projects = db.get_all_projects()
            self.apply_filters()
            # Force table refresh
            self.query_one(ProjectsTable).populate(self.projects)

            # Update detail panel if visible
            if self.info_panel_visible and self.selected_project:
                self.selected_project = next(
                    (p for p in self.all_projects if p.name == self._editing_tags_for),
                    None
                )
                try:
                    detail_panel = self.query_one(DetailPanel)
                    detail_panel.project = self.selected_project
                except Exception:
                    pass

            self.notify(f"Tags updated for {self._editing_tags_for}", severity="information")

    def watch_info_panel_visible(self, visible: bool):
        """React to info panel visibility changes."""
        if visible:
            # Mount the DetailPanel
            if self.selected_project:
                try:
                    panel = DetailPanel()
                    panel.project = self.selected_project
                    self.mount(panel)
                except Exception:
                    pass
        else:
            # Remove the DetailPanel
            try:
                panel = self.query_one(DetailPanel)
                panel.remove()
            except Exception:
                pass

    def watch_selected_project(self, project: Project | None):
        """React to selected project changes."""
        if self.info_panel_visible:
            try:
                detail_panel = self.query_one(DetailPanel)
                detail_panel.project = project
            except Exception:
                pass

    def on_key(self, event: Key):
        """Filter out duplicate/phantom key events."""
        current_time = time.time()
        time_since_last_action = current_time - self._last_action_time
        time_since_last_key = current_time - self._last_key_time

        self._debug_log(f"KEY event: key='{event.key}' time_since_last={time_since_last_action:.3f}s")

        # Detect escape sequence fragments
        # Pattern: '[' followed quickly by A/B/C/D/M/numbers
        # Note: We need to allow valid sequences like Shift+Tab (ESC[Z) through
        is_escape_fragment = False

        # Block '[' only if it appears to be a phantom sequence fragment
        # Don't block it if Textual might need it for valid key sequences
        if event.key == 'left_square_bracket' and self._last_key in ['A', 'B', 'C', 'D', 'M']:
            # This looks like a phantom '[' after arrow/mouse movement
            is_escape_fragment = True
            self._debug_log(f"  -> BLOCKED (phantom '[' after sequence)")

        # Block arrow keys and mouse sequences after '[' (phantom events)
        elif self._last_key == 'left_square_bracket' and time_since_last_key < 0.1:
            if event.key in ['A', 'B', 'C', 'D', 'M', 'semicolon', 'colon'] or event.key.isdigit():
                is_escape_fragment = True
                self._debug_log(f"  -> BLOCKED (part of escape sequence after '[')")

        # Block standalone sequence markers that shouldn't appear
        elif event.key in ['semicolon', 'colon'] and time_since_last_key < 0.1:
            is_escape_fragment = True
            self._debug_log(f"  -> BLOCKED (sequence separator)")

        if is_escape_fragment:
            self._last_key = event.key
            self._last_key_time = current_time
            event.prevent_default()
            event.stop()
            return

        # Update last key tracking
        self._last_key = event.key
        self._last_key_time = current_time

        # Handle 'i' key manually since on_key handler blocks binding resolution
        if event.key == 'i':
            self.action_toggle_info()
            event.prevent_default()
            event.stop()
            return

        # Only allow key events if debounce check passes for action keys
        if event.key in ['1', '2', '3', 'a', 'p', 'c', 'x']:
            if time_since_last_action < self._min_action_interval:
                self._debug_log(f"  -> BLOCKED (too fast, interval={time_since_last_action:.3f}s < {self._min_action_interval}s)")
                event.prevent_default()
                event.stop()
                return
            else:
                self._debug_log(f"  -> ALLOWED")

    def action_add_project(self):
        """Handle add project action."""
        self.app.push_screen(AddProjectModal(), callback=self._on_add_project_complete)

    def _on_add_project_complete(self, result):
        """Handle add project modal dismissal."""
        if result:
            # Reload projects from database
            self.all_projects = db.get_all_projects()
            self.apply_filters()
            # Force table refresh
            self.query_one(ProjectsTable).populate(self.projects)
            self.notify("Project added successfully", severity="information")

    def action_edit_project(self):
        """Handle edit project action."""
        selected = self.query_one(ProjectsTable).get_selected_project()
        if not selected:
            self.notify("No project selected", severity="warning")
            return

        self.app.push_screen(EditProjectModal(selected), callback=self._on_edit_project_complete)

    def _on_edit_project_complete(self, result):
        """Handle edit project modal dismissal."""
        if result:
            # Reload projects from database
            self.all_projects = db.get_all_projects()
            self.apply_filters()
            # Force table refresh
            self.query_one(ProjectsTable).populate(self.projects)
            self.notify("Project updated successfully", severity="information")

    def action_delete_project(self):
        """Handle delete project action."""
        selected = self.query_one(ProjectsTable).get_selected_project()
        if not selected:
            self.notify("No project selected", severity="warning")
            return

        # Store selected project name for the callback
        self._deleting_project_name = selected.name

        # Show confirmation dialog
        self.app.push_screen(
            ConfirmationModal(
                title="Delete Project",
                message=f"Are you sure you want to delete '{selected.name}'?\n\nThis action cannot be undone.",
                confirm_text="Delete",
                cancel_text="Cancel",
                confirm_variant="error"
            ),
            callback=self._on_delete_project_confirm
        )

    def _on_delete_project_confirm(self, result):
        """Handle delete confirmation modal dismissal."""
        if result:
            # Delete the project
            if db.delete_project(self._deleting_project_name):
                # Reload projects from database
                self.all_projects = db.get_all_projects()
                self.apply_filters()
                # Force table refresh
                self.query_one(ProjectsTable).populate(self.projects)
                self.notify(f"Deleted project '{self._deleting_project_name}'", severity="information")
            else:
                self.notify(f"Failed to delete project '{self._deleting_project_name}'", severity="error")

    def action_scan_directory(self):
        """Handle scan directory action."""
        self.app.push_screen(ScanModal(), callback=self._on_scan_complete)

    def _on_scan_complete(self, result):
        """Handle scan modal dismissal."""
        if result:
            # Reload projects from database
            self.all_projects = db.get_all_projects()
            self.apply_filters()
            # Force table refresh
            self.query_one(ProjectsTable).populate(self.projects)
            self.notify("Directory scan completed", severity="information")


# Import Input after the class is defined
from textual.widgets import Input
