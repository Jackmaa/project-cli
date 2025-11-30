"""Projects DataTable widget."""

from textual.widgets import DataTable
from ...models import Project
from ... import display as display_utils


class ProjectsTable(DataTable):
    """Table displaying projects with cursor navigation."""

    def __init__(self):
        super().__init__()
        self.cursor_type = "row"
        self.zebra_stripes = True
        self._projects = []
        self._columns_added = False
        # Disable mouse interactions to prevent accidental triggers
        self.can_focus_children = False

    def populate(self, projects: list[Project]):
        """Populate table with projects."""
        self.clear(columns=False)
        self._projects = projects

        # Add columns only once
        if not self._columns_added:
            self.add_columns(
                "Name", "Status", "Priority", "Lang",
                "Git", "Activity", "Tags"
            )
            self._columns_added = True

        # Add rows
        for project in projects:
            # Format values using existing display utilities
            status_str = f"{display_utils.get_status_emoji(project.status)} {project.status}"
            priority_str = f"{display_utils.get_priority_emoji(project.priority)} {project.priority}"
            git_str = display_utils.format_git_status(project.git_status)
            activity_str = (
                display_utils.format_relative_time(project.last_activity)
                if project.last_activity
                else "never"
            )
            tags_str = ", ".join(project.tags) if project.tags else "-"
            lang_str = project.language or "-"

            self.add_row(
                project.name,
                status_str,
                priority_str,
                lang_str,
                git_str,
                activity_str,
                tags_str,
            )

    def get_selected_project(self) -> Project | None:
        """Get currently selected project."""
        if self.cursor_row < len(self._projects):
            return self._projects[self.cursor_row]
        return None
