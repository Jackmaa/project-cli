"""Main dashboard screen."""

from textual.screen import Screen
from textual.reactive import reactive
from textual.binding import Binding
from textual.events import Click, MouseMove
import subprocess
from pathlib import Path

from ...models import Project
from ... import database as db
from ... import config
from ..widgets import (
    ProjectsTable,
    StatsPanel,
    GitOverview,
    SearchBar,
    QuickActions,
    Footer,
)


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
        Binding("o", "open_ide", "Open"),
        Binding("enter", "open_ide", "Open"),
        Binding("r", "refresh_git", "Refresh"),
        Binding("/", "focus_search", "Search"),
        Binding("q", "quit", "Quit"),
    ]

    # State
    all_projects: list[Project] = []
    projects: reactive[list[Project]] = reactive([])
    search_query: reactive[str] = reactive("")
    status_filter: reactive[str | None] = reactive(None)
    tag_filter: reactive[str | None] = reactive(None)
    priority_filter: reactive[str | None] = reactive(None)

    def compose(self):
        """Compose dashboard layout."""
        yield SearchBar()
        yield StatsPanel()
        yield GitOverview()
        yield ProjectsTable()
        yield QuickActions()
        yield Footer()

    async def on_mount(self):
        """Load data when screen mounts."""
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

    def action_set_status(self, status: str):
        """Handle status change action."""
        selected = self.query_one(ProjectsTable).get_selected_project()
        if not selected:
            self.notify("No project selected", severity="warning")
            return

        if db.update_project_status(selected.name, status):
            selected.status = status
            self.apply_filters()
            self.notify(f"Set {selected.name} to {status}", severity="information")
        else:
            self.notify("Failed to update status", severity="error")

    def action_set_priority(self, priority: str):
        """Handle priority change action."""
        selected = self.query_one(ProjectsTable).get_selected_project()
        if not selected:
            self.notify("No project selected", severity="warning")
            return

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
        """Handle git refresh action."""
        self.notify("Refreshing git status (with remote fetch)...", timeout=2)

        # Update git status for all projects (with fetch enabled)
        for project in self.all_projects:
            if project.path:
                try:
                    db.update_git_status_for_project(project, fetch=True)
                except Exception:
                    pass  # Continue with other projects

        # Reload projects from database
        self.all_projects = db.get_all_projects()
        self.apply_filters()

        self.notify("Git status refreshed", severity="information")

    def action_focus_search(self):
        """Focus the search input."""
        search_input = self.query_one("#search-input", Input)
        search_input.focus()

    def action_quit(self):
        """Quit the application."""
        self.app.exit()

    def on_click(self, event: Click):
        """Prevent mouse clicks from triggering actions."""
        event.prevent_default()
        event.stop()

    def on_mouse_move(self, event: MouseMove):
        """Prevent mouse movements from triggering actions."""
        event.prevent_default()
        event.stop()


# Import Input after the class is defined
from textual.widgets import Input
