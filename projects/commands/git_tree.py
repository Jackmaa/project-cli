"""Git-tree command - Display git commit history as a tree."""

import typer
import subprocess
from typing import Optional
from pathlib import Path

from .. import database as db
from .. import display


def register_command(app: typer.Typer):
    """Register the 'git-tree' command with the Typer app."""

    @app.command(name="git-tree")
    def git_tree(
        name: str = typer.Argument(..., help="Project name"),
        limit: int = typer.Option(20, "--limit", "-n", help="Number of commits to show"),
        all_branches: bool = typer.Option(False, "--all", "-a", help="Show all branches"),
        author: Optional[str] = typer.Option(None, "--author", help="Filter by author"),
    ):
        """
        Display git commit history as a tree (like git log --graph).

        Shows branches, merges, and commit relationships visually.
        """
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

        # Construire la commande git log avec graph
        # Format personnalisé avec couleurs
        git_format = "--pretty=format:%C(yellow)%h%C(reset) - %C(cyan)%ar%C(reset) %C(white)%s%C(reset) %C(dim white)- %an%C(reset)%C(auto)%d%C(reset)"

        git_cmd = [
            "git", "-C", str(path),
            "log",
            "--graph",
            "--decorate",
            git_format,
            f"-{limit}",
        ]

        # Ajouter --all si demandé (toutes les branches)
        if all_branches:
            git_cmd.append("--all")

        # Ajouter le filtre d'auteur si demandé
        if author:
            git_cmd.append(f"--author={author}")

        try:
            # Afficher le titre
            title = f"Git commit tree for '{name}'"
            if all_branches:
                title += " (all branches)"

            display.console.print(f"\n[bold cyan]{title}[/bold cyan]\n")

            # Exécuter git log avec --graph
            # On utilise subprocess.run sans capture pour afficher directement
            result = subprocess.run(
                git_cmd,
                cwd=str(path),
                check=True,
            )

            display.console.print()  # Ligne vide à la fin

        except subprocess.CalledProcessError as e:
            display.print_error("Failed to get git log.")
            raise typer.Exit(1)
        except FileNotFoundError:
            display.print_error("Git is not installed or not in PATH.")
            raise typer.Exit(1)
