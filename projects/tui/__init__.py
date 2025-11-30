"""TUI Dashboard module."""

from .app import ProjectDashboardApp


def run_dashboard():
    """Entry point for TUI dashboard."""
    app = ProjectDashboardApp()
    app.run()


__all__ = ["run_dashboard", "ProjectDashboardApp"]
