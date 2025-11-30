"""Open command - Open a project in IDE."""

import typer
from pathlib import Path
import subprocess

from .. import database as db
from .. import display
from .. import config


def register_command(app: typer.Typer):
    """Register the 'open' command with the Typer app."""

    @app.command()
    def open(name: str = typer.Argument(..., help="Project name")):
        """Open a project in your configured IDE."""
        project = db.get_project(name)

        if not project:
            display.print_error(f"Project '{name}' not found.")
            raise typer.Exit(1)

        if not project.path:
            display.print_error(f"Project '{name}' has no path configured")
            display.print_info(f"Update path with 'projects edit {name} --path /your/path'")
            raise typer.Exit(1)

        path = Path(project.path)
        if not path.exists():
            display.print_error(f"Path does not exist: {project.path}")
            display.print_info(f"Update path with 'projects edit {name} --path /your/path'")
            raise typer.Exit(1)

        # Get or setup IDE
        ide = config.get_ide()
        if not ide:
            display.print_info("No IDE configured. Let's set one up!")
            ide = config.interactive_ide_setup()
            display.print_success(f"IDE configured: {ide}")

        # Open IDE
        try:
            display.print_info(f"Opening {project.name} in {ide}...")
            subprocess.run([ide, str(path)])
            display.print_success(f"Opened {project.name} in {ide}")
        except FileNotFoundError:
            display.print_error(f"IDE '{ide}' not found. Please reconfigure.")
            config.set_ide(None)
            display.print_info("Run 'projects config' to reconfigure your IDE")
            raise typer.Exit(1)
        except Exception as e:
            display.print_error(f"Failed to open IDE: {e}")
            raise typer.Exit(1)
