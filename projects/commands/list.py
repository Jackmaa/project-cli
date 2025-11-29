"""List command - List all projects."""

import typer
from typing import Optional
from enum import Enum

from .. import database as db
from .. import display


class Status(str, Enum):
    """Project status options."""
    active = "active"
    paused = "paused"
    completed = "completed"
    abandoned = "abandoned"


def register_command(app: typer.Typer):
    """Register the 'list' command with the Typer app."""

    @app.command()
    def list(
        status: Optional[Status] = typer.Option(None, "--status", "-s", help="Filter by status"),
        tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag"),
    ):
        """List all projects."""
        status_value = status.value if status else None
        projects = db.get_all_projects(status=status_value, tag=tag)
        display.display_projects_table(projects)
