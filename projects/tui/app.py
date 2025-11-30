"""Main Textual App for project dashboard."""

from textual.app import App
from .screens.dashboard import DashboardScreen


class ProjectDashboardApp(App):
    """TUI Dashboard application for managing projects."""

    CSS_PATH = "styles.css"

    TITLE = "Project Dashboard"
    SUB_TITLE = "Manage your mountain of unfinished projects"

    def on_mount(self):
        """Push dashboard screen on startup."""
        self.push_screen(DashboardScreen())
