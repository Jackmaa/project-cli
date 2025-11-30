"""Git overview widget."""

from textual.reactive import reactive
from textual.widgets import Static
from rich.panel import Panel
from rich.text import Text
from ...models import Project


class GitOverview(Static):
    """Panel displaying git status overview."""

    projects: reactive[list[Project]] = reactive([])

    def watch_projects(self, projects: list[Project]):
        """React to projects list changes."""
        self.update(self.render_git_overview(projects))

    def render_git_overview(self, projects: list[Project]):
        """Render git status overview."""
        counts = {
            "up_to_date": 0,
            "behind": 0,
            "ahead": 0,
            "uncommitted": 0,
            "not_repo": 0,
        }

        for p in projects:
            if not p.git_status or not p.git_status.get("is_repo"):
                counts["not_repo"] += 1
            elif p.git_status.get("uncommitted_changes", 0) > 0:
                counts["uncommitted"] += 1
            elif p.git_status.get("behind", 0) > 0:
                counts["behind"] += 1
            elif p.git_status.get("ahead", 0) > 0:
                counts["ahead"] += 1
            else:
                counts["up_to_date"] += 1

        text = Text()
        text.append("🟢 ", style="green")
        text.append(f"{counts['up_to_date']} up-to-date    ")
        text.append("🔴 ", style="red")
        text.append(f"{counts['behind']} behind\n")
        text.append("🟡 ", style="yellow")
        text.append(f"{counts['uncommitted']} uncommitted  ")
        text.append("⚡ ", style="cyan")
        text.append(f"{counts['ahead']} ahead\n")
        text.append("⚪ ", style="dim")
        text.append(f"{counts['not_repo']} not git repos")

        return Panel(text, title="🌳 Git Status", border_style="green")
