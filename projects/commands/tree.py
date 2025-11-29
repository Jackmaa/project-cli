"""Tree command - Display directory tree structure for a project."""

import typer
from pathlib import Path
from typing import Optional, Set
from rich.tree import Tree
from rich import box

from .. import database as db
from .. import display


def should_ignore(path: Path, ignore_patterns: Set[str]) -> bool:
    """Check if a path should be ignored."""
    # Toujours ignorer certains patterns courants
    default_ignores = {
        ".git", "__pycache__", "node_modules", ".venv", "venv",
        ".idea", ".vscode", "dist", "build", ".next", ".cache",
        "target", "*.pyc", ".DS_Store"
    }

    all_ignores = default_ignores | ignore_patterns

    # Vérifier si le nom correspond à un pattern à ignorer
    for pattern in all_ignores:
        if pattern.startswith("*"):
            # Pattern d'extension (ex: *.pyc)
            ext = pattern[1:]
            if path.suffix == ext:
                return True
        elif path.name == pattern:
            return True

    return False


def build_tree(
    directory: Path,
    tree: Tree,
    max_depth: Optional[int] = None,
    current_depth: int = 0,
    ignore_patterns: Optional[Set[str]] = None,
    show_hidden: bool = False,
):
    """
    Construit récursivement l'arbre des fichiers et dossiers.

    Args:
        directory: Dossier à parcourir
        tree: L'objet Tree de Rich à remplir
        max_depth: Profondeur maximum (None = illimité)
        current_depth: Profondeur actuelle (utilisé en récursion)
        ignore_patterns: Patterns à ignorer
        show_hidden: Afficher les fichiers cachés (commençant par .)
    """
    if ignore_patterns is None:
        ignore_patterns = set()

    # Si on a atteint la profondeur max, arrêter
    if max_depth is not None and current_depth >= max_depth:
        return

    try:
        # Lister tous les éléments du dossier
        items = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name))

        for item in items:
            # Ignorer les fichiers cachés si demandé
            if not show_hidden and item.name.startswith('.'):
                continue

            # Ignorer selon les patterns
            if should_ignore(item, ignore_patterns):
                continue

            # Style selon le type
            if item.is_dir():
                # Dossier: ajouter avec icône et style
                style = "bold cyan"
                label = f"📁 {item.name}"
                branch = tree.add(label, style=style)

                # Récursion pour les sous-dossiers
                build_tree(
                    item,
                    branch,
                    max_depth,
                    current_depth + 1,
                    ignore_patterns,
                    show_hidden,
                )
            else:
                # Fichier: ajouter avec icône selon l'extension
                icon = get_file_icon(item)
                style = "white"
                label = f"{icon} {item.name}"
                tree.add(label, style=style)

    except PermissionError:
        tree.add("❌ [Permission denied]", style="red dim")


def get_file_icon(path: Path) -> str:
    """Retourne une icône selon le type de fichier."""
    ext = path.suffix.lower()

    icons = {
        ".py": "🐍",
        ".js": "📜",
        ".ts": "📘",
        ".tsx": "⚛️",
        ".jsx": "⚛️",
        ".rs": "🦀",
        ".go": "🔵",
        ".java": "☕",
        ".c": "©️",
        ".cpp": "©️",
        ".md": "📝",
        ".txt": "📄",
        ".json": "📋",
        ".yaml": "⚙️",
        ".yml": "⚙️",
        ".toml": "⚙️",
        ".html": "🌐",
        ".css": "🎨",
        ".sh": "🔧",
        ".sql": "🗄️",
        ".png": "🖼️",
        ".jpg": "🖼️",
        ".jpeg": "🖼️",
        ".gif": "🖼️",
        ".svg": "🎨",
    }

    return icons.get(ext, "📄")


def register_command(app: typer.Typer):
    """Register the 'tree' command with the Typer app."""

    @app.command()
    def tree(
        name: str = typer.Argument(..., help="Project name"),
        depth: Optional[int] = typer.Option(None, "--depth", "-d", help="Maximum depth to display"),
        all: bool = typer.Option(False, "--all", "-a", help="Show hidden files"),
    ):
        """Display directory tree structure for a project."""
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

        # Créer l'arbre racine
        root_tree = Tree(
            f"📦 [bold cyan]{project.name}[/bold cyan]",
            guide_style="dim",
        )

        # Construire l'arbre
        build_tree(path, root_tree, max_depth=depth, show_hidden=all)

        # Afficher
        display.console.print(root_tree)
