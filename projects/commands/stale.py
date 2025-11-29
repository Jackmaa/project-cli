"""Stale command - List projects with no activity for a specified number of days."""

import typer
from datetime import datetime, timedelta

from .. import database as db
from .. import display


def register_command(app: typer.Typer):
    """Register the 'stale' command with the Typer app."""

    @app.command()
    def stale(
        days: int = typer.Option(30, "--days", "-d", help="Number of days to consider stale"),
    ):
        """List projects with no activity for a specified number of days."""
        cutoff_date = datetime.now() - timedelta(days=days)

        # Récupérer tous les projets actifs
        projects = db.get_all_projects(status="active")

        # Filtrer ceux qui sont stale
        stale_projects = [
            p for p in projects
            if p.last_activity and p.last_activity < cutoff_date
        ]

        if not stale_projects:
            display.print_success(f"No stale projects found (>{days} days without activity).")
            return

        # Trier par ancienneté
        stale_projects.sort(key=lambda p: p.last_activity if p.last_activity else datetime.min)

        display.print_info(f"Found {len(stale_projects)} stale projects (>{days} days):\n")
        display.display_projects_table(stale_projects)
