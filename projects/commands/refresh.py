"""Refresh command - Refresh git status cache for all projects."""

import typer

from .. import database as db
from .. import display


def register_command(app: typer.Typer):
    """Register the 'refresh' command with the Typer app."""

    @app.command()
    def refresh(
        fetch: bool = typer.Option(
            False,
            "--fetch",
            "-f",
            help="Fetch from remote repositories (may prompt for SSH keys)"
        )
    ):
        """Refresh git status cache for all projects."""
        fetch_msg = " (with remote fetch)" if fetch else ""
        display.print_info(f"Refreshing git status for all projects{fetch_msg}...")

        projects = db.get_all_projects()

        updated_count = 0
        for project in projects:
            if project.path:
                db.update_git_status_for_project(project, fetch=fetch)
                updated_count += 1

        display.print_success(f"Refreshed git status for {updated_count} project(s)")
