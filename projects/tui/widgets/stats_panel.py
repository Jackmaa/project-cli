"""Stats panel widget."""

from textual.reactive import reactive
from textual.widgets import Static
from rich.panel import Panel
from rich.text import Text
from ...models import Project
from ... import display as display_utils


class StatsPanel(Static):
    """Panel displaying project statistics."""

    projects: reactive[list[Project]] = reactive([])

    def watch_projects(self, projects: list[Project]):
        """React to projects list changes."""
        self.update(self.render_stats(projects))

    def render_stats(self, projects: list[Project]):
        """Render statistics."""
        # Count by status
        status_counts = {}
        for p in projects:
            status_counts[p.status] = status_counts.get(p.status, 0) + 1

        # Count by priority
        priority_counts = {}
        for p in projects:
            priority_counts[p.priority] = priority_counts.get(p.priority, 0) + 1

        # Build stats text
        text = Text()
        text.append(f"Total: {len(projects)}\n\n", style="bold cyan")

        text.append("By Status:\n", style="bold")
        for status in ["active", "paused", "completed", "abandoned"]:
            count = status_counts.get(status, 0)
            emoji = display_utils.get_status_emoji(status)
            text.append(f"  {emoji} {status}: {count}\n")

        text.append("\nBy Priority:\n", style="bold")
        for priority in ["high", "medium", "low"]:
            count = priority_counts.get(priority, 0)
            emoji = display_utils.get_priority_emoji(priority)
            text.append(f"  {emoji} {priority}: {count}\n")

        return Panel(text, title="📊 Stats", border_style="blue")
