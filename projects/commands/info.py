"""Info command - Show detailed information about a project."""

import typer

from .. import database as db
from .. import display


def register_command(app: typer.Typer):
    """Register the 'info' command with the Typer app."""

    @app.command()
    def info(name: str = typer.Argument(..., help="Project name")):
        """Show detailed information about a project."""
        project = db.get_project(name)

        if not project:
            display.print_error(f"Project '{name}' not found.")
            raise typer.Exit(1)

        display.display_project_details(project)

        # Show remote metrics if available
        metrics = db.get_metrics_for_project(project.id)
        if metrics:
            remote_info = db.get_remote_repo_info(project.id)
            if remote_info:
                pipeline = db.get_latest_pipeline_status(remote_info['id'])
                print()  # Add spacing
                display.display_remote_metrics(metrics, pipeline, remote_info)
