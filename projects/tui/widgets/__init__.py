"""TUI Widgets for project dashboard."""

from .footer import Footer
from .projects_table import ProjectsTable
from .stats_panel import StatsPanel
from .git_overview import GitOverview
from .search_bar import SearchBar
from .quick_actions import QuickActions

__all__ = [
    "Footer",
    "ProjectsTable",
    "StatsPanel",
    "GitOverview",
    "SearchBar",
    "QuickActions",
]
