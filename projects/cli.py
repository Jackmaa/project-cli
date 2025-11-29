"""CLI interface for project management."""

import typer
from typing import Optional, List
from enum import Enum
from pathlib import Path

from . import database as db
from . import display


app = typer.Typer(
    name="projects",
    help="Manage your mountain of unfinished projects",
    add_completion=False,
    rich_help_panel=False,
)



class Status(str, Enum):
    """Project status options."""

    active = "active"
    paused = "paused"
    completed = "completed"
    abandoned = "abandoned"


class Priority(str, Enum):
    """Project priority options."""

    high = "high"
    medium = "medium"
    low = "low"


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

    # Si un path est fourni, le convertir en Path et d�tecter le langage
    language = None
    if path:
        path_obj = Path(path).expanduser().resolve()
        if path_obj.exists():
            language = detect_language(path_obj)
            path = str(path_obj)
        else:
            display.print_error(f"Path does not exist: {path}")
            raise typer.Exit(1)

    # Ajouter � la DB
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


@app.command()
def list(
    status: Optional[Status] = typer.Option(None, "--status", "-s", help="Filter by status"),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag"),
):
    """List all projects."""
    status_value = status.value if status else None
    projects = db.get_all_projects(status=status_value, tag=tag)
    display.display_projects_table(projects)


@app.command()
def info(name: str = typer.Argument(..., help="Project name")):
    """Show detailed information about a project."""
    project = db.get_project(name)

    if not project:
        display.print_error(f"Project '{name}' not found.")
        raise typer.Exit(1)

    display.display_project_details(project)


@app.command()
def rm(name: str = typer.Argument(..., help="Project name")):
    """Remove a project."""
    # Confirmation
    confirm = typer.confirm(f"Are you sure you want to delete '{name}'?")

    if not confirm:
        display.print_info("Cancelled.")
        raise typer.Abort()

    success = db.delete_project(name)

    if success:
        display.print_success(f"Project '{name}' deleted.")
    else:
        display.print_error(f"Project '{name}' not found.")
        raise typer.Exit(1)


@app.command()
def status(
    name: str = typer.Argument(..., help="Project name"),
    new_status: Status = typer.Argument(..., help="New status"),
):
    """Change the status of a project."""
    success = db.update_project_status(name, new_status.value)

    if success:
        display.print_success(f"Project '{name}' status updated to '{new_status.value}'.")
    else:
        display.print_error(f"Project '{name}' not found.")
        raise typer.Exit(1)


@app.command()
def stats():
    """Show statistics about all projects."""
    stats_data = db.get_stats()
    display.display_stats(stats_data)


@app.command()
def tag(
    name: str = typer.Argument(..., help="Project name"),
    tags_to_add: Optional[str] = typer.Option(None, "--add", "-a", help="Tags to add (comma-separated)"),
    tags_to_remove: Optional[str] = typer.Option(None, "--remove", "-r", help="Tags to remove (comma-separated)"),
):
    """Manage tags for a project."""
    project = db.get_project(name)

    if not project:
        display.print_error(f"Project '{name}' not found.")
        raise typer.Exit(1)

    if tags_to_add:
        add_list = [t.strip() for t in tags_to_add.split(",")]
        db.add_tags(name, add_list)
        display.print_success(f"Added tags to '{name}': {', '.join(add_list)}")

    if tags_to_remove:
        remove_list = [t.strip() for t in tags_to_remove.split(",")]
        db.remove_tags(name, remove_list)
        display.print_success(f"Removed tags from '{name}': {', '.join(remove_list)}")

    if not tags_to_add and not tags_to_remove:
        display.print_info(f"Current tags for '{name}': {', '.join(project.tags) if project.tags else 'none'}")


@app.command()
def edit(
    name: str = typer.Argument(..., help="Project name"),
    new_name: Optional[str] = typer.Option(None, "--name", help="New project name"),
    description: Optional[str] = typer.Option(None, "--desc", "-d", help="New description"),
    priority: Optional[Priority] = typer.Option(None, "--priority", "-p", help="New priority"),
):
    """Edit project details."""
    project = db.get_project(name)

    if not project:
        display.print_error(f"Project '{name}' not found.")
        raise typer.Exit(1)

    # Mettre à jour les champs modifiés
    updated = False

    if new_name:
        success = db.update_project_field(name, "name", new_name)
        if success:
            display.print_success(f"Name updated to '{new_name}'")
            name = new_name  # Pour les updates suivants
            updated = True
        else:
            display.print_error(f"Could not update name (maybe '{new_name}' already exists)")

    if description is not None:
        db.update_project_field(name, "description", description)
        display.print_success(f"Description updated")
        updated = True

    if priority:
        db.update_project_field(name, "priority", priority.value)
        display.print_success(f"Priority updated to '{priority.value}'")
        updated = True

    if not updated:
        display.print_info("No changes specified. Use --name, --desc, or --priority to make changes.")


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


@app.command()
def stale(
    days: int = typer.Option(30, "--days", "-d", help="Number of days to consider stale"),
):
    """List projects with no activity for a specified number of days."""
    from datetime import datetime, timedelta

    cutoff_date = datetime.now() - timedelta(days=days)

    # Récupérer tous les projets actifs
    projects = db.get_all_projects(status="active")

    # Filtrer ceux qui sont stale
    stale_projects = [
        p for p in projects
        if p.last_activity and p.last_activity < cutoff_date
    ]

    if not stale_projects:
        display.print_success(f"No stale projects found (>{days} days without activity).")
        return

    # Trier par ancienneté
    stale_projects.sort(key=lambda p: p.last_activity if p.last_activity else datetime.min)

    display.print_info(f"Found {len(stale_projects)} stale projects (>{days} days):\n")
    display.display_projects_table(stale_projects)


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


def get_last_git_activity(path: Path) -> Optional:
    """Get the date of the last commit in a git repository."""
    import subprocess
    from datetime import datetime

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
    # Map d'extensions vers langages
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

    # Compter les fichiers par extension
    extension_counts = {}

    try:
        for file in path.rglob("*"):
            if file.is_file():
                ext = file.suffix.lower()
                if ext in language_map:
                    extension_counts[ext] = extension_counts.get(ext, 0) + 1
    except PermissionError:
        pass

    # Retourner le langage le plus fr�quent
    if extension_counts:
        most_common_ext = max(extension_counts, key=extension_counts.get)
        return language_map[most_common_ext]

    return None


# Point d'entr�e pour Poetry
if __name__ == "__main__":
    app()
