"""Log command - Track and display activity log for projects."""

import typer
from datetime import datetime
from typing import Optional
from pathlib import Path
from rich.table import Table
from rich import box

from .. import database as db
from .. import display


def register_command(app: typer.Typer):
    """Register the 'log' command with the Typer app."""

    @app.command()
    def log(
        name: Optional[str] = typer.Argument(None, help="Project name (optional, shows all if not provided)"),
        limit: int = typer.Option(20, "--limit", "-n", help="Number of log entries to show"),
        add: Optional[str] = typer.Option(None, "--add", "-a", help="Add a log entry"),
    ):
        """
        Track and display activity log for projects.

        Examples:
            projects log my-project              # Show logs for a specific project
            projects log                         # Show logs for all projects
            projects log my-project --add "Fixed bug in auth"
        """
        # Si on veut ajouter une entrée de log
        if add:
            if not name:
                display.print_error("You must specify a project name when adding a log entry.")
                raise typer.Exit(1)

            project = db.get_project(name)
            if not project:
                display.print_error(f"Project '{name}' not found.")
                raise typer.Exit(1)

            # Ajouter l'entrée de log
            success = db.add_log_entry(name, add)

            if success:
                display.print_success(f"Log entry added to '{name}'.")
            else:
                display.print_error("Failed to add log entry.")
            return

        # Sinon, afficher les logs
        if name:
            # Logs pour un projet spécifique
            project = db.get_project(name)
            if not project:
                display.print_error(f"Project '{name}' not found.")
                raise typer.Exit(1)

            logs = db.get_project_logs(name, limit=limit)
            title = f"Activity log for '{name}'"
        else:
            # Logs pour tous les projets
            logs = db.get_all_logs(limit=limit)
            title = "Recent activity (all projects)"

        if not logs:
            display.print_info("No log entries found.")
            return

        # Afficher dans une table
        table = Table(title=title, box=box.ROUNDED)

        if not name:
            # Si on affiche tous les projets, ajouter une colonne projet
            table.add_column("Project", style="cyan", no_wrap=True)

        table.add_column("Date", style="dim")
        table.add_column("Activity", style="white")

        for log_entry in logs:
            timestamp = datetime.fromisoformat(log_entry["timestamp"])
            relative_time = display.format_relative_time(timestamp)
            date_str = f"{timestamp.strftime('%Y-%m-%d %H:%M')} ({relative_time})"

            if not name:
                table.add_row(log_entry["project_name"], date_str, log_entry["message"])
            else:
                table.add_row(date_str, log_entry["message"])

        display.console.print(table)
