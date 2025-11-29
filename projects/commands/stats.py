"""Stats command - Show statistics about all projects."""

import typer

from .. import database as db
from .. import display


def register_command(app: typer.Typer):
    """Register the 'stats' command with the Typer app."""

    @app.command()
    def stats():
        """Show statistics about all projects."""
        stats_data = db.get_stats()
        display.display_stats(stats_data)
