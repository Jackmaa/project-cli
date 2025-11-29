"""Edit command - Edit project details."""

import typer
from typing import Optional
from enum import Enum

from .. import database as db
from .. import display


class Priority(str, Enum):
    """Project priority options."""
    high = "high"
    medium = "medium"
    low = "low"


def register_command(app: typer.Typer):
    """Register the 'edit' command with the Typer app."""

    @app.command()
    def edit(
        name: str = typer.Argument(..., help="Project name"),
        new_name: Optional[str] = typer.Option(None, "--name", help="New project name"),
        description: Optional[str] = typer.Option(None, "--desc", "-d", help="New description"),
        priority: Optional[Priority] = typer.Option(None, "--priority", "-p", help="New priority"),
    ):
        """Edit project details."""
        project = db.get_project(name)

        if not project:
            display.print_error(f"Project '{name}' not found.")
            raise typer.Exit(1)

        # Mettre à jour les champs modifiés
        updated = False

        if new_name:
            success = db.update_project_field(name, "name", new_name)
            if success:
                display.print_success(f"Name updated to '{new_name}'")
                name = new_name  # Pour les updates suivants
                updated = True
            else:
                display.print_error(f"Could not update name (maybe '{new_name}' already exists)")

        if description is not None:
            db.update_project_field(name, "description", description)
            display.print_success(f"Description updated")
            updated = True

        if priority:
            db.update_project_field(name, "priority", priority.value)
            display.print_success(f"Priority updated to '{priority.value}'")
            updated = True

        if not updated:
            display.print_info("No changes specified. Use --name, --desc, or --priority to make changes.")
