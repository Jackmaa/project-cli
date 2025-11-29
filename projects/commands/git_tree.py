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
        oneline: bool = typer.Option(False, "--oneline", "-o", help="Compact one-line format"),
        stat: bool = typer.Option(False, "--stat", "-s", help="Show file change statistics"),
    ):
        """
        Display git commit history as a tree (like git log --graph).

        Shows branches, merges, and commit relationships visually with enhanced styling.
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
        # Format personnalisé avec couleurs et emojis
        if oneline:
            # Format compact sur une ligne
            git_format = "--pretty=format:%C(auto)%h%C(reset) %C(bold)%s%C(reset) %C(dim)(%ar)%C(reset)%C(auto)%d%C(reset)"
        else:
            # Format détaillé avec plus d'infos
            git_format = (
                "--pretty=format:"
                "%C(bold yellow)◉ %h%C(reset) "
                "%C(auto)%d%C(reset)%n"
                "  %C(bold white)%s%C(reset)%n"
                "  %C(blue)✎ %an%C(reset) "
                "%C(green)✔ %ar%C(reset) "
                "%C(dim)(%ad)%C(reset)"
            )

        git_cmd = [
            "git", "-C", str(path),
            "log",
            "--graph",
            "--decorate",
            "--date=format:%Y-%m-%d %H:%M",
            git_format,
            f"-{limit}",
        ]

        # Ajouter --all si demandé (toutes les branches)
        if all_branches:
            git_cmd.append("--all")

        # Ajouter le filtre d'auteur si demandé
        if author:
            git_cmd.append(f"--author={author}")

        # Ajouter les stats si demandé
        if stat:
            git_cmd.append("--stat")

        try:
            # Afficher le titre avec un header plus sexy
            title_parts = [f"🌳 Git Tree: [bold magenta]{name}[/bold magenta]"]

            options = []
            if all_branches:
                options.append("[cyan]all branches[/cyan]")
            if author:
                options.append(f"[yellow]author: {author}[/yellow]")
            if oneline:
                options.append("[green]compact[/green]")
            if stat:
                options.append("[blue]with stats[/blue]")

            if options:
                title_parts.append(f"({', '.join(options)})")

            title = " ".join(title_parts)
            display.console.print(f"\n{title}")
            display.console.print("─" * 80 + "\n")

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
