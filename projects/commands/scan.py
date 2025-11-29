"""Scan command - Scan a directory for git repositories and add them as projects."""

import typer
import subprocess
from typing import Optional, List
from pathlib import Path
from datetime import datetime

from .. import database as db
from .. import display


def scan_directory(base_path: Path, max_depth: Optional[int] = None) -> List[Path]:
    """Find all git repositories in a directory."""
    repos = []

    def walk(path: Path, depth: int):
        if max_depth and depth > max_depth:
            return

        if not path.is_dir():
            return

        # Si c'est un repo git, l'ajouter et ne pas descendre plus profond
        if is_git_repo(path):
            repos.append(path)
            return

        # Sinon continuer la recherche
        try:
            for child in path.iterdir():
                if child.is_dir() and not child.name.startswith('.'):
                    walk(child, depth + 1)
        except PermissionError:
            pass  # Ignorer les dossiers non accessibles

    walk(base_path, 0)
    return repos


def is_git_repo(path: Path) -> bool:
    """Check if a directory is a git repository."""
    return (path / ".git").exists()


def get_last_git_activity(path: Path) -> Optional[datetime]:
    """Get the date of the last commit in a git repository."""
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "log", "-1", "--format=%ct"],
            capture_output=True,
            text=True,
            check=True,
        )
        timestamp = int(result.stdout.strip())
        return datetime.fromtimestamp(timestamp)
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        return None


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
    """Register the 'scan' command with the Typer app."""

    @app.command()
    def scan(
        directory: str = typer.Argument(..., help="Directory to scan for git repos"),
        depth: Optional[int] = typer.Option(None, "--depth", "-d", help="Maximum depth to scan"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be imported without adding"),
    ):
        """Scan a directory for git repositories and add them as projects."""
        base_path = Path(directory).expanduser().resolve()

        if not base_path.exists():
            display.print_error(f"Directory does not exist: {directory}")
            raise typer.Exit(1)

        if not base_path.is_dir():
            display.print_error(f"Not a directory: {directory}")
            raise typer.Exit(1)

        display.print_info(f"Scanning {base_path} for git repositories...")

        # Scanner le dossier
        repos = scan_directory(base_path, depth)

        if not repos:
            display.print_info("No git repositories found.")
            return

        display.print_info(f"Found {len(repos)} git repositories.")

        # Pour chaque repo, l'importer
        imported = 0
        skipped = 0

        for repo_path in repos:
            name = repo_path.name
            language = detect_language(repo_path)
            last_activity = get_last_git_activity(repo_path)

            if dry_run:
                status_str = "Would import"
                lang_str = f"Language: {language}" if language else "Language: unknown"
                activity_str = f"Last activity: {last_activity}" if last_activity else "No activity"
                display.print_info(f"  {status_str}: {name} ({lang_str}, {activity_str})")
            else:
                # Vérifier si le projet existe déjà
                existing = db.get_project(name)
                if existing:
                    skipped += 1
                    continue

                # Ajouter le projet
                success = db.add_project(
                    name=name,
                    path=str(repo_path),
                    language=language,
                    last_activity=last_activity,
                )

                if success:
                    imported += 1
                    display.print_success(f"  Imported: {name}")
                else:
                    skipped += 1

        if not dry_run:
            display.print_success(f"\nImported {imported} projects, skipped {skipped}.")
