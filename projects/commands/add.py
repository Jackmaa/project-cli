"""Add command - Add a new project to the database."""

import typer
from typing import Optional
from pathlib import Path
from enum import Enum

from .. import database as db
from .. import display


class Priority(str, Enum):
    """Project priority options."""
    high = "high"
    medium = "medium"
    low = "low"


def detect_language(path: Path) -> Optional[str]:
    """Detect the primary language in a project directory."""
    language_map = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".jsx": "JavaScript",
        ".tsx": "TypeScript",
        ".rs": "Rust",
        ".go": "Go",
        ".java": "Java",
        ".c": "C",
        ".cpp": "C++",
        ".cs": "C#",
        ".rb": "Ruby",
        ".php": "PHP",
        ".swift": "Swift",
        ".kt": "Kotlin",
        ".dart": "Dart",
        ".vue": "Vue",
        ".html": "HTML",
        ".css": "CSS",
        ".sh": "Shell",
    }

    extension_counts = {}

    try:
        for file in path.rglob("*"):
            if file.is_file():
                ext = file.suffix.lower()
                if ext in language_map:
                    extension_counts[ext] = extension_counts.get(ext, 0) + 1
    except PermissionError:
        pass

    if extension_counts:
        most_common_ext = max(extension_counts, key=extension_counts.get)
        return language_map[most_common_ext]

    return None


def register_command(app: typer.Typer):
    """Register the 'add' command with the Typer app."""

    @app.command()
    def add(
        name: str = typer.Argument(..., help="Project name"),
        description: Optional[str] = typer.Option(None, "--desc", "-d", help="Project description"),
        path: Optional[str] = typer.Option(None, "--path", "-p", help="Path to project directory"),
        priority: Priority = typer.Option(Priority.medium, "--priority", help="Project priority"),
        tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Comma-separated tags"),
    ):
        """Add a new project."""
        # Parser les tags
        tag_list = [t.strip() for t in tags.split(",")] if tags else []

        # Si un path est fourni, le convertir en Path et détecter le langage
        language = None
        if path:
            path_obj = Path(path).expanduser().resolve()
            if path_obj.exists():
                language = detect_language(path_obj)
                path = str(path_obj)
            else:
                display.print_error(f"Path does not exist: {path}")
                raise typer.Exit(1)

        # Ajouter à la DB
        success = db.add_project(
            name=name,
            description=description,
            path=path,
            priority=priority.value,
            language=language,
            tags=tag_list,
        )

        if success:
            display.print_success(f"Project '{name}' added successfully!")
        else:
            display.print_error(f"Project '{name}' already exists.")
            raise typer.Exit(1)
