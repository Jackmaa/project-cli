"""Centralized keyboard bindings management."""

from textual.binding import Binding


class KeyBindings:
    """Central registry for all keyboard bindings."""

    # Status changes
    STATUS_BINDINGS = [
        Binding("a", "set_status('active')", "Active"),
        Binding("p", "set_status('paused')", "Pause"),
        Binding("c", "set_status('completed')", "Complete"),
        Binding("x", "set_status('abandoned')", "Abandon"),
    ]

    # Priority changes
    PRIORITY_BINDINGS = [
        Binding("1", "set_priority('high')", "High"),
        Binding("2", "set_priority('medium')", "Medium"),
        Binding("3", "set_priority('low')", "Low"),
    ]

    # Project-level actions
    PROJECT_ACTIONS = [
        Binding("i", "show_info", "Info"),
        Binding("t", "manage_tags", "Tags"),
        Binding("e", "edit_project", "Edit"),
        Binding("d", "delete_project", "Delete"),
        Binding("o", "open_ide", "Open"),
        Binding("enter", "open_ide", "Open"),
    ]

    # Git operations
    GIT_OPERATIONS = [
        Binding("g,c", "show_commits", "Commits"),
        Binding("g,h", "show_github", "GitHub"),
        Binding("g,t", "show_git_tree", "Git Tree"),
        Binding("g,l", "show_logs", "Logs"),
    ]

    # Dashboard-level actions
    DASHBOARD_ACTIONS = [
        Binding("s", "scan_projects", "Scan"),
        Binding("ctrl+r", "refresh_git", "Refresh"),
        Binding("ctrl+s", "show_config", "Config"),
        Binding("f", "show_stale", "Stale"),
    ]

    # Navigation
    NAVIGATION = [
        Binding("/", "focus_search", "Search"),
        Binding("escape", "clear_search", "Clear"),
        Binding("q", "quit", "Quit"),
    ]

    @classmethod
    def get_all_bindings(cls):
        """Get all bindings combined."""
        return (
            cls.STATUS_BINDINGS +
            cls.PRIORITY_BINDINGS +
            cls.PROJECT_ACTIONS +
            cls.GIT_OPERATIONS +
            cls.DASHBOARD_ACTIONS +
            cls.NAVIGATION
        )
