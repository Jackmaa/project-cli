"""Commits command - Show git commit history for a project."""

import typer
import subprocess
from typing import Optional
from pathlib import Path
from rich.table import Table
from rich import box

from .. import database as db
from .. import display


def register_command(app: typer.Typer):
    """Register the 'commits' command with the Typer app."""

    @app.command()
    def commits(
        name: str = typer.Argument(..., help="Project name"),
        limit: int = typer.Option(10, "--limit", "-n", help="Number of commits to show"),
        author: Optional[str] = typer.Option(None, "--author", "-a", help="Filter by author"),
    ):
        """Show git commit history for a project."""
        # Récupérer le projet
        project = db.get_project(name)

        if not project:
            display.print_error(f"Project '{name}' not found.")
            raise typer.Exit(1)

        if not project.path:
            display.print_error(f"Project '{name}' has no path set.")
            raise typer.Exit(1)

        path = Path(project.path)
        if not path.exists():
            display.print_error(f"Path does not exist: {project.path}")
            raise typer.Exit(1)

        # Vérifier si c'est un repo git
        if not (path / ".git").exists():
            display.print_error(f"'{name}' is not a git repository.")
            raise typer.Exit(1)

        # Construire la commande git log
        # Format: hash court | date | auteur | message
        git_format = "--pretty=format:%h|%ar|%an|%s"
        git_cmd = ["git", "-C", str(path), "log", git_format, f"-{limit}"]

        # Ajouter le filtre d'auteur si demandé
        if author:
            git_cmd.append(f"--author={author}")

        try:
            result = subprocess.run(
                git_cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            commits_output = result.stdout.strip()

            if not commits_output:
                display.print_info(f"No commits found for '{name}'.")
                return

            # Parser et afficher dans une table
            table = Table(title=f"Commits for '{name}'", box=box.ROUNDED)
            table.add_column("Hash", style="cyan", no_wrap=True)
            table.add_column("Date", style="dim")
            table.add_column("Author", style="magenta")
            table.add_column("Message", style="white")

            for line in commits_output.split("\n"):
                if not line:
                    continue

                parts = line.split("|", maxsplit=3)
                if len(parts) == 4:
                    commit_hash, date, author_name, message = parts
                    table.add_row(commit_hash, date, author_name, message)

            display.console.print(table)

        except subprocess.CalledProcessError as e:
            display.print_error(f"Failed to get git log: {e.stderr}")
            raise typer.Exit(1)
        except FileNotFoundError:
            display.print_error("Git is not installed or not in PATH.")
            raise typer.Exit(1)
