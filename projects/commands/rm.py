"""Remove command - Remove a project."""

import typer

from .. import database as db
from .. import display


def register_command(app: typer.Typer):
    """Register the 'rm' command with the Typer app."""

    @app.command()
    def rm(name: str = typer.Argument(..., help="Project name")):
        """Remove a project."""
        # Confirmation
        confirm = typer.confirm(f"Are you sure you want to delete '{name}'?")

        if not confirm:
            display.print_info("Cancelled.")
            raise typer.Abort()

        success = db.delete_project(name)

        if success:
            display.print_success(f"Project '{name}' deleted.")
        else:
            display.print_error(f"Project '{name}' not found.")
            raise typer.Exit(1)
