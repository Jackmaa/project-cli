"""Tag command - Manage tags for a project."""

import typer
from typing import Optional

from .. import database as db
from .. import display


def register_command(app: typer.Typer):
    """Register the 'tag' command with the Typer app."""

    @app.command()
    def tag(
        name: str = typer.Argument(..., help="Project name"),
        tags_to_add: Optional[str] = typer.Option(None, "--add", "-a", help="Tags to add (comma-separated)"),
        tags_to_remove: Optional[str] = typer.Option(None, "--remove", "-r", help="Tags to remove (comma-separated)"),
    ):
        """Manage tags for a project."""
        project = db.get_project(name)

        if not project:
            display.print_error(f"Project '{name}' not found.")
            raise typer.Exit(1)

        if tags_to_add:
            add_list = [t.strip() for t in tags_to_add.split(",")]
            db.add_tags(name, add_list)
            display.print_success(f"Added tags to '{name}': {', '.join(add_list)}")

        if tags_to_remove:
            remove_list = [t.strip() for t in tags_to_remove.split(",")]
            db.remove_tags(name, remove_list)
            display.print_success(f"Removed tags from '{name}': {', '.join(remove_list)}")

        if not tags_to_add and not tags_to_remove:
            display.print_info(f"Current tags for '{name}': {', '.join(project.tags) if project.tags else 'none'}")
