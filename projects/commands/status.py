"""Status command - Change the status of a project."""

import typer
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
    """Register the 'status' command with the Typer app."""

    @app.command()
    def status(
        name: str = typer.Argument(..., help="Project name"),
        new_status: Status = typer.Argument(..., help="New status"),
    ):
        """Change the status of a project."""
        success = db.update_project_status(name, new_status.value)

        if success:
            display.print_success(f"Project '{name}' status updated to '{new_status.value}'.")
        else:
            display.print_error(f"Project '{name}' not found.")
            raise typer.Exit(1)
