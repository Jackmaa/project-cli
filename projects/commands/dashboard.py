"""Dashboard command - Launch interactive TUI dashboard."""

import typer


def register_command(app: typer.Typer):
    """Register the 'dashboard' command with the Typer app."""

    @app.command()
    def dashboard():
        """Launch interactive TUI dashboard for project management."""
        from ..tui import run_dashboard

        run_dashboard()
