"""CLI interface for project management."""

import typer

# Créer l'app Typer
app = typer.Typer(
    name="projects",
    help="Manage your mountain of unfinished projects",
    add_completion=False,
    rich_help_panel=False,
)


# Charger dynamiquement toutes les commandes depuis le dossier commands/
from .commands import load_commands

load_commands(app)


# Point d'entrée pour Poetry
if __name__ == "__main__":
    app()
